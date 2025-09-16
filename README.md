# AiStock
sector_rotation/               # 主项目目录
│── main.py                    # 主入口，每日执行分析，写入数据库
│── config.py                  # 配置文件（权重参数、日期范围等）
│
├── data/                      # 数据层 (Data Layer) - 调用 AKShare
│   ├── board_data.py          # 获取板块列表 & 成分股
│   ├── board_price.py         # 板块行情数据
│   ├── board_money.py         # 板块资金流数据
│   ├── board_hot.py           # 板块人气数据
│   └── stock_data.py          # 个股行情 & 龙虎榜
│
├── factors/                   # 因子层 (Factor Layer)
│   ├── trend_factor.py        # 涨幅、均线、超额收益
│   ├── hype_factor.py         # 成交额、换手率、人气
│   ├── capital_factor.py      # 资金净流入、主力流入
│   ├── leader_factor.py       # 龙头股识别
│   └── rotation_factor.py     # RPS: 补涨、资金承接、人气传导、技术准备
│
├── models/                    # 模型层 (Model Layer)
│   ├── strong_board.py        # 强势板块打分模型
│   └── rps_predict.py         # 板块轮动预测模型 (RPS)
│
├── strategy/                  # 策略层 (Strategy Layer)
│   ├── board_selection.py     # 板块选择逻辑
│   ├── stock_selection.py     # 候选龙头股选择
│   └── position_control.py    # 仓位管理 (Regime)
│
├── reports/                   # 执行层 (Execution Layer)
│   ├── daily_report.py        # 生成每日报告 (表格/控制台输出)
│   └── visualization.py       # 可视化 (资金流、轮动路径图)
│
├── db/                        # 数据库存储层 (Database Layer)
│   ├── database.py            # 数据库连接封装 (SQLite/Postgres/MySQL)
│   ├── schema.sql             # 建表语句
│   └── writer.py              # 写入分析结果
│
├── scheduler/                 # 任务调度层 (Scheduler)
│   └── daily_task.py          # 每日定时调度（调用 main.py）
│
└── utils/                     # 工具层 (Utils)
    ├── akshare_helper.py      # AKShare 通用接口封装
    ├── indicators.py          # 技术指标计算（均线、MACD等）
    └── logger.py              # 日志工具
