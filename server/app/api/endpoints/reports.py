from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response

from ...deps import get_reports_store
from ...models.reports import Report, ReportCreate, ReportUpdate
from ...services.reports_store import ReportsStore


router = APIRouter()


@router.get("", response_model=List[Report], summary="List all reports")
def list_reports(store: ReportsStore = Depends(get_reports_store)) -> list[Report]:
    return store.list_reports()


@router.post("", response_model=Report, summary="Create a new report")
def create_report(
    body: ReportCreate,
    store: ReportsStore = Depends(get_reports_store),
) -> Report:
    return store.create_report(body)


@router.get("/{report_id}", response_model=Report, summary="Get a report by id")
def get_report(
    report_id: str,
    store: ReportsStore = Depends(get_reports_store),
) -> Report:
    report = store.get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.put("/{report_id}", response_model=Report, summary="Update a report")
def update_report(
    report_id: str,
    body: ReportUpdate,
    store: ReportsStore = Depends(get_reports_store),
) -> Report:
    report = store.update_report(report_id, body)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.delete("/{report_id}", status_code=204, summary="Delete a report")
def delete_report(
    report_id: str,
    store: ReportsStore = Depends(get_reports_store),
) -> Response:
    deleted = store.delete_report(report_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Report not found")
    return Response(status_code=204)

