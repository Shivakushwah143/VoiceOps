"""Deterministic policy, deliberately independent of provider SDKs and persistence."""
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid')

class ToolRequest(Strict):
    name: Literal['add_call_note','update_lead','schedule_demo','create_followup','set_call_outcome','opt_out_contact']
    args: dict

class Decision(Strict):
    speak: str = Field(min_length=1, max_length=1600)
    tool: ToolRequest | None = None
    end_call: bool = False

class Note(Strict):
    note: str = Field(min_length=1,max_length=2000)
class Update(Strict):
    interest: str | None = Field(default=None,max_length=500)
    status: Literal['NEW','CONTACTED','QUALIFIED','NOT_INTERESTED','CLOSED'] | None = None
class MeetingArgs(Strict):
    purpose: str = Field(min_length=1,max_length=500)
    start_at: datetime
    timezone: str
    duration_minutes: int = Field(ge=15,le=120)
class FollowupArgs(Strict):
    purpose: str = Field(min_length=1,max_length=500)
    due_at: datetime
    timezone: str
class OutcomeArgs(Strict):
    outcome: Literal['INTERESTED','NOT_INTERESTED','DEMO_SCHEDULED','FOLLOWUP_REQUESTED','OPTED_OUT','UNRESOLVED']
class OptoutArgs(Strict):
    reason: str = Field(min_length=1,max_length=500)
TOOL_SCHEMAS = {'add_call_note':Note,'update_lead':Update,'schedule_demo':MeetingArgs,'create_followup':FollowupArgs,'set_call_outcome':OutcomeArgs,'opt_out_contact':OptoutArgs}

class Summary(Strict):
    summary: str = Field(max_length=3000)
    interest: str = Field(max_length=500)
    objections: list[str]
    commitments: list[str]
    suggested_next_steps: list[str]

TERMINAL = {'COMPLETED','FAILED','CANCELLED','NO_ANSWER','BUSY','REJECTED'}
TRANSITIONS = {
 'CREATED':{'QUEUED','DIALING','CONNECTED','REJECTED','CANCELLED','FAILED'},
 'QUEUED':{'DIALING','CANCELLED','REJECTED','FAILED'},
 'DIALING':{'RINGING','CONNECTED','BUSY','NO_ANSWER','REJECTED','FAILED','CANCELLED'},
 'RINGING':{'CONNECTED','BUSY','NO_ANSWER','REJECTED','FAILED','CANCELLED'},
 'CONNECTED':{'ACTIVE','ENDING'},'ACTIVE':{'ENDING'},'ENDING':{'COMPLETED','FAILED','CANCELLED'}}

def valid_phone(value):
    if not re.fullmatch(r'\+[1-9][0-9]{7,14}',value):
        raise ValueError('Use an E.164 number such as +<country><number>')
    return value

def explicit_optout(text):
    return bool(re.search(r"\b(don['’]?t call me|do not call me|stop calling|remove me from (your|the) (call|contact|phone|marketing)|no more calls|unsubscribe)\b", text, re.I))

def affirmative(text):
    return bool(re.fullmatch(r'\s*(yes|yes please|confirm|confirmed|that is correct|go ahead)[.! ]*',text,re.I))

def valid_time(value, zone):
    if value.tzinfo is None or value.utcoffset() != value.astimezone(ZoneInfo(zone)).utcoffset():
        raise ValueError('Explicit matching date, offset and IANA timezone required')
    if value <= datetime.now(timezone.utc):
        raise ValueError('Time must be in the future')
    return value
