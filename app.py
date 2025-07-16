import pandas as pd

# ==== 基本參數 ====
current_age = 25
target_ages = list(range(25, 66, 5))  # 每年試算不同退休年齡
monthly_expense_today = 80000
inflation_rate = 0.02
annual_return = 0.08
death_age = 90
extra_annual_contribution = 100000  # 每年 1 月額外投入金額

# ==== 新增：目前投資情況 ====
initial_assets = 500000        # 現有資產（例如已存50萬）
monthly_investment = 34000     # 每月投資金額

# ==== 計算實質報酬率（考慮通膨） ====
real_return_rate = (1 + annual_return) / (1 + inflation_rate) - 1

# ==== 表格資料 ====
data = []

# ==== 主試算迴圈 ====
for retire_age in target_ages:
    invest_years = retire_age - current_age
    retirement_years = death_age - retire_age
    if invest_years <= 0 or retirement_years <= 0:
        continue

    # 通膨調整後的退休支出
    adj_monthly_expense = monthly_expense_today * ((1 + inflation_rate) ** invest_years)
    adj_annual_expense = adj_monthly_expense * 12

    # 退休所需資產
    needed_assets = adj_annual_expense * (1 - (1 + real_return_rate) ** -retirement_years) / real_return_rate

    # 計算投資期間的月報酬率
    monthly_return = (1 + annual_return) ** (1 / 12) - 1
    months_to_invest = invest_years * 12

    # 年加碼部分的未來總值
    extra_contribution_future_value = sum([
        extra_annual_contribution * ((1 + monthly_return) ** (months_to_invest - 12 * i))
        for i in range(invest_years)
    ])

    # 剩下缺口靠月投資補足
    required_from_monthly = needed_assets - extra_contribution_future_value
    if required_from_monthly < 0:
        monthly_required = 0
    else:
        monthly_required = required_from_monthly / (((1 + monthly_return) ** months_to_invest - 1) / monthly_return)

    data.append({
        "退休年齡": retire_age,
        "投資年數": invest_years,
        "退休年數": retirement_years,
        "退休當年每月支出（元）": round(adj_monthly_expense, 0),
        "退休所需資產（元）": round(needed_assets, 0),
        "每月需投資金額（元）": round(monthly_required, 0)
    })

# ==== 建立 DataFrame 並輸出 ====
df_retirement = pd.DataFrame(data)

# 表頭格式
header_format = "{:<5} {:<5} {:<10} {:<5} {:<5} {:<5}"
row_format =    "{:<10} {:<10} {:<14} {:<20,.0f} {:<20,.0f} {:<18,.0f}"

print(header_format.format("退休年齡", "投資年數", "退休年數", "退休當年每月支出（元）", "退休所需資產（元）", "每月需投資金額（元）"))
print("-" * 100)

for _, row in df_retirement.iterrows():
    print(row_format.format(
        int(row["退休年齡"]),
        int(row["投資年數"]),
        int(row["退休年數"]),
        row["退休當年每月支出（元）"],
        row["退休所需資產（元）"],
        row["每月需投資金額（元）"]
    ))

# ==== 新增功能：試算多久可以達到退休所需金額 ====
def calculate_years_to_retire(
    current_age,
    initial_assets,
    monthly_investment,
    extra_annual_contribution,
    target_assets,
    annual_return
):
    current_assets = initial_assets
    month = 0
    monthly_return = (1 + annual_return) ** (1 / 12) - 1

    while current_assets < target_assets and month < 100 * 12:
        if month % 12 == 0:
            current_assets += extra_annual_contribution
        current_assets *= (1 + monthly_return)
        current_assets += monthly_investment
        month += 1

    if current_assets >= target_assets:
        years = month // 12
        months = month % 12
        return years, months, round(current_assets)
    else:
        return None, None, round(current_assets)

# ==== 執行範例試算（以退休年齡 60 為目標） ====
target_age_to_test = 45
target_row = df_retirement[df_retirement["退休年齡"] == target_age_to_test]

if not target_row.empty:
    target_assets = target_row.iloc[0]["退休所需資產（元）"]
    years, months, final_assets = calculate_years_to_retire(
        current_age=current_age,
        initial_assets=initial_assets,
        monthly_investment=monthly_investment,
        extra_annual_contribution=extra_annual_contribution,
        target_assets=target_assets,
        annual_return=annual_return
    )

    print("\n📈 達成退休資產試算（目標退休年齡：{} 歲）".format(target_age_to_test))
    if years is not None:
        print(f"✅ 你將在 {years} 年 {months} 個月後達到目標退休資產（{target_assets:,.0f} 元）")
        print(f"💰 屆時預估資產：{final_assets:,.0f} 元")
        print(f"🎉 預估年齡：{current_age + years} 歲 {months} 個月")
    else:
        print("❌ 無法在合理年限內達成退休目標。請增加投資或延後退休年齡。")
else:
    print(f"找不到退休年齡 {target_age_to_test} 的試算資料。")
