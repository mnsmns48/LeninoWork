from pandas import DataFrame, ExcelWriter
from sqlalchemy import Table, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from engine import ssh_connect
from models import LeninoWork


def write_data(session: Session, table: Table, data: list | dict):
    session.execute(insert(table).values(data).on_conflict_do_update(
        index_elements=['id'], set_=dict(updated_at=data.get('updated_at')))
    )
    session.commit()


@ssh_connect
def output(**kwargs):
    query = select(LeninoWork.title,
                   LeninoWork.author,
                   LeninoWork.payment,
                   LeninoWork.cond,
                   LeninoWork.desc,
                   LeninoWork.performance,
                   LeninoWork.locality,
                   LeninoWork.link,
                   LeninoWork.updated_at).order_by(LeninoWork.updated_at.desc())
    with Session(bind=kwargs.get('bind').engine) as session:
        data = session.execute(query)
        result = data.all()
    df = DataFrame(result)
    writer = ExcelWriter('data_new.xlsx')
    try:
        df.to_excel(writer, index=False)
    finally:
        writer.close()
        print('ready')
