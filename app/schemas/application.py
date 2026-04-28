from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from app.models.application import ApplicationSource, ApplicationStatus, RemoteType


class ApplicationBase(BaseModel):
    company_name: str = Field(min_length=1, max_length=180)
    job_title: str = Field(min_length=1, max_length=220)
    job_url: HttpUrl | None = None
    location: str | None = Field(default=None, max_length=180)
    remote_type: RemoteType = RemoteType.REMOTE
    salary_min: float | None = Field(default=None, ge=0)
    salary_max: float | None = Field(default=None, ge=0)
    currency: str | None = Field(default="USD", min_length=3, max_length=3)
    status: ApplicationStatus = ApplicationStatus.SAVED
    source: ApplicationSource = ApplicationSource.OTHER
    notes: str | None = Field(default=None, max_length=10000)
    applied_at: date | None = None
    follow_up_date: date | None = None

    @model_validator(mode="after")
    def validate_salary_range(self):
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError("salary_min must be less than or equal to salary_max")
        return self


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=1, max_length=180)
    job_title: str | None = Field(default=None, min_length=1, max_length=220)
    job_url: HttpUrl | None = None
    location: str | None = Field(default=None, max_length=180)
    remote_type: RemoteType | None = None
    salary_min: float | None = Field(default=None, ge=0)
    salary_max: float | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    status: ApplicationStatus | None = None
    source: ApplicationSource | None = None
    notes: str | None = Field(default=None, max_length=10000)
    applied_at: date | None = None
    follow_up_date: date | None = None


class ApplicationRead(BaseModel):
    id: str
    user_id: str
    company_name: str
    job_title: str
    job_url: str | None
    location: str | None
    remote_type: RemoteType
    salary_min: float | None
    salary_max: float | None
    currency: str | None
    status: ApplicationStatus
    source: ApplicationSource
    notes: str | None
    applied_at: date | None
    follow_up_date: date | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
