import pytest
from app.nodes import route_by_grade, route_after_approval

#route_by_grade: hot·warm·cold test with parametrize
@pytest.mark.parametrize("grade, expected",[
    ("hot", "draft_reply"),
    ("warm","schedule_followup"),
    ("cold", "log_only"),
])

def test_route_by_grade(grade, expected):
    assert route_by_grade({"grade": grade}) == expected

#route_by_grade ValueError → pytest.raises(ValueError)
def test_unknown_grade_raised():
    with pytest.raises(ValueError):
        route_by_grade({"grade": "maybe"})


#route_after_approval의 approved·modify → "send" (parametrize)
@pytest.mark.parametrize("approval, expected",[
    ("approved", "send"),
    ("modify", "send"),
])
def test_after_approval(approval, expected):
    assert route_after_approval({"approval": approval}) == expected

#route_after_approval by rejected → "end"
def test_after_approval_rejected():
    assert route_after_approval({"approval": "rejected"}) == "end"
