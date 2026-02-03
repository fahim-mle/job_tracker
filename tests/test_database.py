from datetime import date, datetime

import pytest
from sqlalchemy import Enum as SAEnum
from sqlalchemy import UniqueConstraint, inspect as sa_inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.sqltypes import (
    Boolean,
    Date,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)

from src.database.models import Application, Job, JobSkill, Skill


def _sample_value(column):
    column_type = column.type
    if isinstance(column_type, SAEnum):
        return list(column_type.enums)[0] if column_type.enums else "enum"
    if isinstance(column_type, (String, Text)):
        return f"{column.name}-value"
    if isinstance(column_type, Integer):
        return 1
    if isinstance(column_type, Float):
        return 1.0
    if isinstance(column_type, Boolean):
        return True
    if isinstance(column_type, DateTime):
        return datetime.utcnow()
    if isinstance(column_type, Date):
        return date.today()
    return f"{column.name}-value"


def _build_instance(model, **overrides):
    mapper = sa_inspect(model)
    data = {}
    for column in mapper.columns:
        if column.name in overrides:
            continue
        if column.primary_key and (
            column.autoincrement
            or column.default is not None
            or column.server_default is not None
        ):
            continue
        if (
            column.nullable
            or column.default is not None
            or column.server_default is not None
        ):
            continue
        data[column.name] = _sample_value(column)
    data.update(overrides)
    return model(**data)


def _single_primary_key_value(instance):
    pk_columns = sa_inspect(instance.__class__).primary_key
    if len(pk_columns) != 1:
        raise ValueError("Only single-column primary keys are supported")
    return getattr(instance, pk_columns[0].name)


def _primary_key_values(instance):
    return [
        getattr(instance, col.name)
        for col in sa_inspect(instance.__class__).primary_key
    ]


def _relationship_to(mapper, target_class):
    for rel in mapper.relationships:
        if rel.mapper.class_ is target_class:
            return rel.key
    return None


def _fk_column_to(mapper, target_table):
    for column in mapper.columns:
        for fk in column.foreign_keys:
            if fk.column.table.name == target_table.name:
                return column.name
    return None


def _is_column_unique(column):
    if column.unique:
        return True
    for constraint in column.table.constraints:
        if isinstance(constraint, UniqueConstraint) and list(constraint.columns) == [
            column
        ]:
            return True
    for index in column.table.indexes:
        if index.unique and list(index.columns) == [column]:
            return True
    return False


def _unique_url_column(job_mapper):
    for column in job_mapper.columns:
        if "url" not in column.name.lower():
            continue
        if _is_column_unique(column):
            return column
    return None


def test_create_job(db_session):
    job = _build_instance(Job)
    db_session.add(job)
    db_session.commit()

    assert _single_primary_key_value(job) is not None


def test_create_application_for_job(db_session):
    job = _build_instance(Job)
    db_session.add(job)
    db_session.flush()

    app_mapper = sa_inspect(Application)
    job_mapper = sa_inspect(Job)
    application_kwargs = {}

    rel_key = _relationship_to(app_mapper, Job)
    if rel_key:
        application_kwargs[rel_key] = job
    else:
        fk_column = _fk_column_to(app_mapper, job_mapper.local_table)
        if fk_column:
            application_kwargs[fk_column] = _single_primary_key_value(job)
        else:
            pytest.skip("Application has no relationship or FK to Job")

    application = _build_instance(Application, **application_kwargs)
    db_session.add(application)
    db_session.commit()

    assert _single_primary_key_value(application) is not None


def test_create_skill_and_link_via_job_skill(db_session):
    job = _build_instance(Job)
    skill = _build_instance(Skill)
    db_session.add_all([job, skill])
    db_session.flush()

    link_mapper = sa_inspect(JobSkill)
    job_mapper = sa_inspect(Job)
    skill_mapper = sa_inspect(Skill)
    link_kwargs = {}

    job_rel = _relationship_to(link_mapper, Job)
    if job_rel:
        link_kwargs[job_rel] = job
    else:
        job_fk = _fk_column_to(link_mapper, job_mapper.local_table)
        if job_fk:
            link_kwargs[job_fk] = _single_primary_key_value(job)
        else:
            pytest.skip("JobSkill has no relationship or FK to Job")

    skill_rel = _relationship_to(link_mapper, Skill)
    if skill_rel:
        link_kwargs[skill_rel] = skill
    else:
        skill_fk = _fk_column_to(link_mapper, skill_mapper.local_table)
        if skill_fk:
            link_kwargs[skill_fk] = _single_primary_key_value(skill)
        else:
            pytest.skip("JobSkill has no relationship or FK to Skill")

    link = _build_instance(JobSkill, **link_kwargs)
    db_session.add(link)
    db_session.commit()

    assert _primary_key_values(link)
    assert all(value is not None for value in _primary_key_values(link))


def test_unique_job_url_constraint(db_session):
    job_mapper = sa_inspect(Job)
    url_column = _unique_url_column(job_mapper)
    if url_column is None:
        pytest.skip("No unique URL column defined on Job")

    url_value = "https://example.com/jobs/unique"
    job = _build_instance(Job, **{url_column.name: url_value})
    db_session.add(job)
    db_session.commit()

    duplicate = _build_instance(Job, **{url_column.name: url_value})
    db_session.add(duplicate)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
