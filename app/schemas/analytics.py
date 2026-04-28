from pydantic import BaseModel


class AnalyticsOverview(BaseModel):
    total_applications: int
    average_salary_min: float | None
    average_salary_max: float | None
    upcoming_follow_ups: int
    applications_created_this_week: int
    applications_created_this_month: int


class AnalyticsBucket(BaseModel):
    key: str
    count: int
