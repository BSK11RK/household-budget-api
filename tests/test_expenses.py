def test_create_expense(client):
    res = client.post(
        "/expenses",
        json={
            "title": "スーパー",
            "amount": 1200,
            "category": "食費",
            "expense_date": "2026-10-18"
        }
    )
    
    assert res.status_code in (200, 201)
    
    data = res.json()
    
    assert data["title"] == "スーパー"
    assert data["amount"] == 1200
    assert data["category"] == "食費"
    assert data["user_id"] == 1
    

def test_monthly_report_includes_expense(client):
    create_res = client.post(
        "/expenses",
        json={
            "title": "スーパー",
            "amount": 1200,
            "category": "食費",
            "expense_date": "2026-10-18"
        }
    )
    
    assert create_res.status_code in (200, 201)
    
    # 2026年10月の月次レポートを取得
    res = client.get(
        "/reports/monthly",
        params={"year": 2026, "month": 10}
    )
    
    assert res.status_code == 200
    
    data = res.json()
    
    assert data["expense_total"] == 1200
    assert data["balance"] == -1200
    
    
def test_create_budget(client):
    res = client.post(
        "/budgets",
        json={
            "year": 2026,
            "month": 10,
            "category": "食費",
            "amount": 30000
        }
    )
    
    assert res.status_code in (200, 201)
    
    data = res.json()
    
    assert data["year"] == 2026
    assert data["month"] == 10
    assert data["category"] == "食費"
    assert data["amount"] == 30000
    assert data["user_id"] == 1