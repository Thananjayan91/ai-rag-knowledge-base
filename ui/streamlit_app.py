import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(page_title="AI RAG Knowledge Base", page_icon="📚")
st.title("📚 AI RAG Knowledge Base")


def fetch_projects():
    response = requests.get(f"{API_URL}/projects", timeout=5)
    return response.json() if response.ok else []


with st.sidebar:
    st.header("Project")

    try:
        projects = fetch_projects()
    except requests.exceptions.RequestException:
        st.error(
            f"Can't reach the API at {API_URL}. Is `uvicorn app.main:app --reload` "
            "running in another terminal?"
        )
        st.stop()

    with st.expander("+ New project"):
        new_name = st.text_input("Project name", key="new_project_name")
        if st.button("Create project"):
            response = requests.post(f"{API_URL}/projects", json={"name": new_name}, timeout=5)
            if response.ok:
                st.success(f"Created '{response.json()['name']}'")
                st.rerun()
            else:
                st.error(response.json().get("detail", "Failed to create project"))

    if not projects:
        st.info("Create a project above to get started.")
        st.stop()

    project_names = [p["name"] for p in projects]
    selected_name = st.selectbox("Active project", project_names)
    selected_slug = next(p["slug"] for p in projects if p["name"] == selected_name)

    if st.session_state.get("confirm_delete") == selected_slug:
        st.warning(f"Delete '{selected_name}' and all its indexed documents? This can't be undone.")
        confirm_col, cancel_col = st.columns(2)
        with confirm_col:
            if st.button("Yes, delete", type="primary"):
                response = requests.delete(f"{API_URL}/projects/{selected_slug}", timeout=30)
                st.session_state.pop("confirm_delete", None)
                if response.ok:
                    st.rerun()
                else:
                    st.error(response.json().get("detail", "Delete failed"))
        with cancel_col:
            if st.button("Cancel"):
                st.session_state.pop("confirm_delete", None)
                st.rerun()
    else:
        if st.button("Delete project"):
            st.session_state["confirm_delete"] = selected_slug
            st.rerun()

    st.divider()
    st.header("Upload documents")
    uploaded_files = st.file_uploader(
        "PDF, DOCX, or TXT — select as many as you like",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )
    if uploaded_files and st.button(f"Index {len(uploaded_files)} document(s)"):
        progress = st.progress(0.0)
        total_chunks = 0
        failures = []
        for i, uploaded_file in enumerate(uploaded_files):
            with st.spinner(f"Indexing {uploaded_file.name}..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                data = {"project": selected_slug}
                response = requests.post(
                    f"{API_URL}/documents/upload", files=files, data=data, timeout=120
                )
            if response.ok:
                total_chunks += response.json()["chunks_indexed"]
            else:
                failures.append((uploaded_file.name, response.json().get("detail", "failed")))
            progress.progress((i + 1) / len(uploaded_files))
        if total_chunks:
            st.success(
                f"Indexed {total_chunks} chunks across "
                f"{len(uploaded_files) - len(failures)} file(s)"
            )
        for name, detail in failures:
            st.error(f"{name}: {detail}")

st.header(f"Ask a question — {selected_name}")
question = st.text_input("Your question")
if question and st.button("Ask"):
    with st.spinner("Thinking..."):
        response = requests.post(
            f"{API_URL}/ask",
            json={"project": selected_slug, "question": question},
            timeout=60,
        )
    if response.ok:
        data = response.json()
        st.markdown(f"**Answer:** {data['answer']}")
        if data["sources"]:
            st.markdown("**Sources:**")
            for source in data["sources"]:
                location = f"page {source['page']}" if source["page"] else "document"
                st.markdown(
                    f"- {source['filename']} ({location}) — "
                    f"similarity {source['score']}, rerank {source['rerank_score']}"
                )
        else:
            st.caption("Nothing was retrieved for this question — the project's index may be empty.")
    else:
        st.error(response.json().get("detail", "Request failed"))
