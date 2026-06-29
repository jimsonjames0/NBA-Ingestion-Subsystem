from src.transform import create_matchKey, add_matchKey, build_gameLookup


def test_create_matchkey():
    key = create_matchKey(
        "2025-04-11",
        "Los Angeles Lakers",
        "Houston Rockets"
    )

    assert key == "20250411_LOS_HOU"


def test_missing_game():

    games=[]

    logs=[{"Game_ID":"123"}]

    result = add_matchKey(logs,games)

    assert result == logs


def test_lookup():

    games = [
        {
            "gameId":1,
            "matchKey":"ABC",
            "gameDate":"2025-01-01"
        }
    ]

    lookup = build_gameLookup(games)

    assert lookup[1]["matchKey"] == "ABC"

def test_add_matchkey():

    games = [
        {
            "gameId":100,
            "matchKey":"20250401_LAL_BOS",
            "gameDate":"2025-04-01"
        }
    ]

    logs = [
        {
            "Game_ID":"100"
        }
    ]

    result = add_matchKey(logs,games)

    assert result[0]["matchKey"] == "20250401_LAL_BOS"