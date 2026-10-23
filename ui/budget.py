"""Locale-independent budget editing; only whole-INR amounts are accepted."""
from decimal import Decimal
from pathlib import Path
import re
import streamlit as st

def parse_budget(text: str) -> int:
    if not re.fullmatch(r'\d+(?:\.\d{0,7})?', text.strip()):
        raise ValueError('Use a period, with up to 7 decimal places (whole INR).')
    amount=Decimal(text.strip())
    if not Decimal(0)<=amount<=Decimal(100):
        raise ValueError('Enter a budget from 0 to 100 crore.')
    return int(amount*10_000_000)

_control=st.components.v2.component('civic_decimal_budget',html='<div class="budget-field"><label for="capital-budget">Capital budget · INR crore</label><input id="capital-budget" type="text" inputmode="decimal" autocomplete="off" aria-describedby="budget-help budget-error"><small id="budget-help">0–100 crore · Enter or leave the field to apply; Escape restores.</small><small id="budget-error" role="alert"></small></div>',js=(Path(__file__).with_name('budget.js')).read_text(encoding='utf-8'),isolate_styles=False)

def budget_input():
    st.session_state.setdefault('budget_text','2')
    result=_control(
        key='capital_budget',
        data={'value':st.session_state.get('budget_draft',st.session_state['budget_text']),
              'committed':st.session_state['budget_text']},
        default={'value':st.session_state.get('budget_draft',st.session_state['budget_text'])},
        on_value_change=lambda:None,
        height="content",
    )
    if result.value is not None:
        text=result.value
        st.session_state['budget_draft']=text
        try:
            parse_budget(text)
            st.session_state['budget_text']=text
        except ValueError:
            pass
    try:
        return parse_budget(st.session_state.get('budget_draft',st.session_state['budget_text']))
    except ValueError:
        return None
