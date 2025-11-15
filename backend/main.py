import io
from fastapi import FastAPI, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

# --- FIXED: use absolute imports instead of relative ---
from tools.pdf_tools import markdown_from_paper, generate_pdf_from_text
from agents.orchestrator import Orchestrator

# -------------------------------------------------------

app = FastAPI(title="Agentic Research Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()


# -----------------------------------------
# RUN PIPELINE (accept mode query param)
# -----------------------------------------
@app.post('/run')
async def run_research(background_tasks: BackgroundTasks, mode: str = Query("default")):
    """
    Start pipeline. Optional query param `mode`:
      - default
      - explore
      - summarize
      - simulate
    Example: POST /run?mode=explore
    """
    run_id = orchestrator.start(mode=mode)
    return {"run_id": run_id, "status": "started", "mode": mode}


# -----------------------------------------
# CHECK STATUS
# -----------------------------------------
@app.get('/status/{run_id}')
async def status(run_id: str):
    return orchestrator.get_status(run_id)


# -----------------------------------------
# GET RESULT
# -----------------------------------------
@app.get('/result/{run_id}')
async def result(run_id: str):
    return orchestrator.get_result(run_id)


# -----------------------------------------
# DOWNLOAD RESULT (Markdown / PDF)
# -----------------------------------------
@app.get('/result/{run_id}/download')
def download_result(run_id: str, format: str = "md"):
    """
    Downloads the generated paper.
    format = 'md' or 'pdf'
    """
    paper = orchestrator.get_result(run_id)
    if not paper:
        return JSONResponse({"error": "run_id not found"}, status_code=404)

    # Convert to Markdown
    md = markdown_from_paper(paper)

    # -------- Markdown download --------
    if format == "md":
        b = io.BytesIO(md.encode("utf-8"))
        headers = {"Content-Disposition": f"attachment; filename=paper_{run_id}.md"}
        return StreamingResponse(b, media_type="text/markdown", headers=headers)

    # -------- PDF download --------
    elif format == "pdf":
        try:
            pdf_bytes = generate_pdf_from_text(md)
        except Exception as e:
            return JSONResponse(
                {"error": "PDF generation failed", "detail": str(e)},
                status_code=500,
            )
        b = io.BytesIO(pdf_bytes)
        headers = {"Content-Disposition": f"attachment; filename=paper_{run_id}.pdf"}
        return StreamingResponse(b, media_type="application/pdf", headers=headers)

    # -------- Invalid format --------
    else:
        return JSONResponse({"error": "unsupported format"}, status_code=400)
