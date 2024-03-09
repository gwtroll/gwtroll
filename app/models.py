from datetime import datetime, timezone, date, timedelta
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

class Registrations(db.Model):
    regid: so.Mapped[int] = so.mapped_column(primary_key=True)
    order_id: so.Mapped[Optional[int]]
    fname: so.Mapped[str] 
    lname: so.Mapped[str] 
    scaname: so.Mapped[Optional[str]] 
    kingdom: so.Mapped[Optional[str]] 
    event_ticket: so.Mapped[Optional[str]] 
    rate_mbr: so.Mapped[Optional[str]] 
    rate_age: so.Mapped[Optional[str]] 
    rate_date: so.Mapped[Optional[str]] 
    price_calc: so.Mapped[Optional[int]]
    price_paid: so.Mapped[Optional[int]]
    price_due: so.Mapped[Optional[int]]
    lodging: so.Mapped[Optional[str]] 
    pay_type: so.Mapped[Optional[str]]
    prereg_status: so.Mapped[Optional[str]] 
    mbr_num_exp: so.Mapped[Optional[str]] 
    mbr_num: so.Mapped[Optional[int]]
    mbr_exp: so.Mapped[Optional[date]]
    requests: so.Mapped[Optional[str]] 
    checkin: so.Mapped[Optional[datetime]]
    medallion: so.Mapped[Optional[int]]
    reg_date_time: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now().replace(microsecond=0).isoformat())

    def __repr__(self):
        return '<Registrations {}>'.format(self.regid)