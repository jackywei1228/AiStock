import logging
from datetime import date

from ai_stock import AnalysisConfig, run_daily_analysis
from ai_stock.sector_rotation.data import board_data, stock_data
from ai_stock.sector_rotation.factors import leader_factor
from ai_stock.sector_rotation.models.strong_board import BoardScore
from ai_stock.sector_rotation.factors.leader_factor import LeaderCandidate
from ai_stock.sector_rotation.strategy.stock_selection import select_leaders

# ---------- 配置 ----------
target_date = date(2025, 10, 13)
# 今天
# target_date =  date.today()
top_board_count = 10
rps_top_n = 3
leaders_per_board = 5
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
# -------------------------

config = AnalysisConfig.daily_defaults(target_date)
config.board_count = top_board_count
config.leaders_per_board = leaders_per_board

result = run_daily_analysis(config)

rotation_candidates = result["rotation_candidates"][:rps_top_n]
if not rotation_candidates:
    print("No rotation candidates for", target_date)
    raise SystemExit

print(f"RPS Top {len(rotation_candidates)} boards for {target_date}:")
for idx, cand in enumerate(rotation_candidates, start=1):
    print(f"{idx}. {cand['board']} ({cand['name']}): readiness={cand['predicted']:.2f}")
print()

# 重新为 RPS 候选板块计算龙头（使用分析区间 end_date 的历史行情）
candidate_codes = [cand["board"] for cand in rotation_candidates]
board_map = {board.code: board for board in board_data.list_boards(limit=config.board_count)}
focused_boards = [board_map[code] for code in candidate_codes if code in board_map]

# 拉取这批候选板块的成员 + 历史行情
members = {board.code: board_data.list_board_members(board) for board in focused_boards}
symbols = {symbol for lst in members.values() for symbol in lst}

stock_history = stock_data.fetch_stock_data(symbols, config.start_date, config.end_date)

board_quotes = {
    board.code: stock_data.fetch_board_component_quotes(
        board,
        limit=80,
        history=stock_history,
        target_date=config.end_date,
        members=members.get(board.code),
    )
    for board in focused_boards
}

leader_map, _ = leader_factor.calculate_leader_factor(
    board_quotes, stock_history, top_n=leaders_per_board
)

# 输出结果
for board in focused_boards:
    picks = leader_map.get(board.code, [])[:leaders_per_board]
    print(f"{board.code} ({board.name}) top {len(picks)} stocks:")
    if not picks:
        print("  (no candidates)")
        continue
    for pick in picks:
        price = pick.name  # we only have name in LeaderCandidate
        label = f"{pick.symbol}({pick.name})"
        print(
            f"  - {label:<18} 价格 {pick.return_pct*100+100:>8.2f}?  "
            f"涨幅 {pick.pct_change:>6.1f}%  成交占比 {pick.turnover_share*100:>6.1f}%"
            f"{' 涨停' if pick.is_limit_up else ''}"
        )
    print()

print("Factor Table:")
print(result["factor_table"])
print("\nRotation Path:")
print(result["rotation_path"])