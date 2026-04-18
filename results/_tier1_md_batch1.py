import json, datetime

tz_offset = datetime.timezone(datetime.timedelta(hours=8))
now = datetime.datetime.now(tz_offset).isoformat()

entries = [
    {
        "source_file": "E:/投資交易/研究與模型/backtest_framework_spec.md",
        "source_tag": "tier1_md",
        "timestamp": now,
        "domain": "systematic_trading",
        "title": "台指期回測框架規格 + Edward交易模式",
        "key_concepts": [
            "Python自建回測引擎（非backtrader/zipline），完全控制MAE/MFE計算",
            "IS/OOS淘汰標準：MDD_OOS/MDD_IS>2.0x淘汰，Sharpe_OOS/Sharpe_IS<0.5淘汰，勝率方向翻轉直接淘汰",
            "模組設計：data/loader → strategy/base → engine/runner → metrics/stats+oos → report/summary",
            "Edward交易四階段：市場分類器→順勢+避險→逆勢回歸→選擇權→跨市場",
            "理想權益曲線=階梯狀（下跌空手，上漲滿倉）",
            "數據來源：Yahoo Finance日K（免費驗證），嘉實/精誠分K（上線用）"
        ],
        "formulas": {
            "OOS_IS_MDD_threshold": "MDD_OOS/MDD_IS > 2.0x 淘汰",
            "OOS_IS_Sharpe_threshold": "Sharpe_OOS/Sharpe_IS < 0.5 淘汰"
        },
        "summary": "台指期策略回測系統設計規格。Python自建引擎，重點在IS/OOS淘汰標準（MDD比>2x或Sharpe比<0.5即淘汰）。Edward四階段交易模式：市場分類→順勢避險→逆勢→選擇權→跨市場，長期目標覆蓋agent運行成本。"
    },
    {
        "source_file": "E:/投資交易/研究與模型/FI_model_template.md",
        "source_tag": "tier1_md",
        "timestamp": now,
        "domain": "financial_independence",
        "title": "FI財務獨立模型模板",
        "key_concepts": [
            "FI核心參數：月收入I、每日消費c、名目年報酬r、通膨i、初始資產W0",
            "FI閾值W*：投資組合大到足以由報酬支應所有消費",
            "可行條件：r>i 且 收入>支出",
            "月支出M=c*30.4375，月儲蓄S=I-M，實質報酬rho=(r-i)/(1+i)"
        ],
        "summary": "FI財務獨立計算模板。輸入月收入、每日消費、報酬率、通膨率及初始資產，計算達到FI所需月數及FI門檻。可行條件：實質報酬>0且收入>支出。"
    },
    {
        "source_file": "E:/投資交易/研究與模型/財神爺框架.md",
        "source_tag": "tier1_md",
        "timestamp": now,
        "domain": "alternative_data",
        "title": "財神爺框架：用戶瀏覽數據預測股價",
        "key_concepts": [
            "核心假設：鉅亨網用戶瀏覽行為領先股價（瀏覽量↑成交量↑股價）",
            "假設可測試：特定個股當日被大量瀏覽→隔日均價漲幅？",
            "特徵工程：用戶ID+日期+股票代碼+停留時間→隔日均價漲跌幅",
            "模型架構：歷史資料→訓練預測模型（今日走勢+隔日走勢）→即時資料→模擬操盤",
            "今日走勢=(收盤-開盤)/開盤；隔日均價漲跌幅=(明日均價-今日收盤)/今日收盤"
        ],
        "summary": "另類數據應用案例。以鉅亨網用戶瀏覽數據為特徵，預測個股隔日走勢。核心假設：股價大跌→瀏覽量增加；瀏覽量與成交量正相關。建立今日走勢模型+隔日走勢模型進行模擬操盤。"
    },
    {
        "source_file": "E:/投資交易/量化金融文獻/知識素材/MAFE 基本五步驟流程.md",
        "source_tag": "tier1_md",
        "timestamp": now,
        "domain": "strategy_optimization",
        "title": "MAE/MFE分析五步驟流程",
        "key_concepts": [
            "A. 觀察策略波動穩定性：MAE/MFE時序圖，判斷是否需分段分析",
            "B. 判斷是否需延遲進場：右上角MAE高MFE低→延遲進場；參考MAE Q1~(Q1+Q2)/2",
            "C. 停損停利設定：波段交易看MAE對MFEbeforeMAE圖；趨勢交易看MAE對MFE圖；SL/TP會消耗勝率",
            "D. 移動停損：觀察MHL；損益兩平觸發點設在敗手MFE (Q1+Q2)/2~Q2",
            "E. 加減碼：高勝率→不利方向加碼在WinMAE Q1~Q2；MFE高→有利方向加碼在WinMFE Q2~Q3",
            "原則：法則非唯一，需依策略特性調整"
        ],
        "summary": "MAE/MFE分析實用五步驟：穩定性觀察→延遲進場判斷→SL/TP設定→移動停損→加減碼機制。每步驟有具體的分布圖觀察方法和分位數參考值。"
    },
    {
        "source_file": "E:/投資交易/量化金融文獻/知識素材/MAFE 最大幅度分析法.md",
        "source_tag": "tier1_md",
        "timestamp": now,
        "domain": "strategy_optimization",
        "title": "MAE/MFE最大幅度分析法基礎",
        "key_concepts": [
            "MAE=Max Adverse Excursion=持倉期間最大不利幅度（含交易成本）；MFE=Max Favorable Excursion",
            "cMFE=全程最大有利幅度；MFE before MAE=MAE之前的最大有利幅度（可用停利）",
            "E-Ratio=MFE/MAE=邊際優勢比；策略體質指標",
            "勝手(winning trade)MAE：無長尾，前段bins叢聚快速遞減；敗手MAE：有長尾，峰值在勝手右側",
            "MAE分布形狀：正偏=策略體質好；負偏=過早進場；多峰=市場波動水準變化",
            "停損選取：找勝手/敗手MAE的切分點，或以資金1%作為bin size",
            "新手應先使MAE變小，才能透過交易績效衡量策略"
        ],
        "summary": "MAE/MFE分析法基礎定義與應用。重點：MAE決定停損位置（非技術指標），勝手MAE無長尾、敗手MAE有長尾，從分布找最優切點。E-Ratio=MFE/MAE衡量策略優勢。先解決MAE再優化MFE。"
    },
    {
        "source_file": "E:/投資交易/量化金融文獻/知識素材/MAFE 進階分析.md",
        "source_tag": "tier1_md",
        "timestamp": now,
        "domain": "strategy_optimization",
        "title": "MAE/MFE進階分析：ATR標準化、時間維度、多貨幣兌",
        "key_concepts": [
            "ATR標準化：MAE/MFE單位改用當下Daily ATR，消除不同波動水準差異",
            "時間維度MAE/MFE：進場N個bar內的MAE vs 之後的MAE（海龜Edge-Ratio）",
            "多組合MAE/MFE：以整組損益計算MAE/MFE，而非單標的價格",
            "反向單層級：MAE→MFEbeforeMAE→MAE before MFEbeforeMAE，越細緻越複雜",
            "進場lot size與SL關係：ATR小時SL縮小→可能增加部位；需平衡穩定損益與工業化風險管理",
            "ML預測迷思：LSTM不優於ARIMA，spectral bias導致只能擬合低頻，overfitting根本是樣本代表性"
        ],
        "summary": "MAE/MFE進階優化方向：用ATR標準化消除波動差異、加入時間維度edge-ratio、多組合整體計算。ML預測警告：LSTM不優於ARIMA，spectral bias導致只能擬合低頻，overfitting根本是樣本代表性問題。"
    },
    {
        "source_file": "E:/投資交易/量化金融文獻/知識素材/A Model of Momentum.md",
        "source_tag": "tier1_md",
        "timestamp": now,
        "domain": "asset_pricing",
        "title": "Liu & Zhang 2011 NBER: 動量的投資理論模型",
        "key_concepts": [
            "核心命題：動量利潤可由neoclassical投資理論（非行為偏誤）解釋",
            "機制：Winners有更高expected growth + expected marginal productivity → 更高expected stock returns",
            "模型alpha：winner-minus-loser=0.44%/yr vs CAPM 16.95% vs FF3F 19.15%",
            "比較靜態：expected I/K growth是動量最重要驅動因子；expected sales/capital次之",
            "動量反轉：2年後自然反轉，原因是expected I/K growth低持久性",
            "交叉效應：模型捕捉size、age、volume、volatility與動量的交互作用",
            "模型缺陷：無法複製procyclical動量利潤（景氣好時動量更強）"
        ],
        "summary": "NBER WP16747。動量利潤可由最優投資理論解釋，無需行為偏誤假設。Winners有更高投資成長率和邊際生產力→更高預期報酬。GMM估計alpha僅0.44%/yr。動量2年後反轉因I/K growth持久性低。"
    },
    {
        "source_file": "E:/投資交易/量化金融文獻/知識素材/Mechanics of Futures Markets & Hedging Using Futures.md",
        "source_tag": "tier1_md",
        "timestamp": now,
        "domain": "derivatives_futures",
        "title": "期貨市場機制與避險策略",
        "key_concepts": [
            "期貨特性：集中交易、每日結算（marking to market）、標準化合約",
            "保證金機制：原始保證金→每日結算損益→維持保證金→Margin call→變動保證金",
            "交割日：First notice day / Last notice day / Last trading day；多頭需在first notice day前平倉",
            "期貨vs遠期：標準化/每日結算/無信用風險 vs 客製化/到期結算/有信用風險",
            "基差風險(Basis risk)：欲避險標的與期貨標的不同、時間不同、需提前平倉",
            "避險爭論：公司不應替股東避險（股東可自己避）vs 本業公司應鎖定非本業風險",
            "空頭/多頭避險；產業競爭者不避險時，一家避險反而收益不穩定",
            "正常市場(contango)=遠月>近月；反轉市場(backwardation)=近月>遠月（便利收益yield）",
            "TAIFEX在FIA交易量排名第17，台指選擇權排名第13"
        ],
        "summary": "期貨市場基礎機制：每日結算、保證金制度、基差風險。避險策略：空頭避險（持現貨賣期貨）/多頭避險（放空現貨買期貨）。正常/反轉市場結構。重要：公司避險必須考慮整個產業生態，否則反效果。"
    },
    {
        "source_file": "E:/投資交易/量化金融文獻/知識素材/Option Introduction.md",
        "source_tag": "tier1_md",
        "timestamp": now,
        "domain": "derivatives_options",
        "title": "選擇權入門：基本概念與策略",
        "key_concepts": [
            "Call Payoff = Max{0, S-K}；Put Payoff = Max{0, K-S}",
            "選擇權價值 = 內含價值(intrinsic value) + 時間價值(time value)",
            "ITM=有內含價值(Call:S>K, Put:K>S)；OTM=無內含價值；ATM=S=K",
            "買方：虧損有限（權利金），獲利無限，希望波動大",
            "賣方：獲利有限（最多收權利金），虧損無限，希望波動小，需繳保證金",
            "BTC選擇權以BTC計價結算，PnL與vanilla option不同（需除以到期標的價格）",
            "參數：標的價格、履約價K、到期時間τ=T-t、權利金c/p"
        ],
        "summary": "選擇權基礎。Call=有權買(S-K)^+；Put=有權賣(K-S)^+。買方付權利金換無限獲利潛力；賣方收權利金承擔無限風險。BTC選擇權特殊：以BTC結算，PnL計算需換算。"
    },
    {
        "source_file": "E:/投資交易/量化金融文獻/交易策略與系統規範.md",
        "source_tag": "tier1_md",
        "timestamp": now,
        "domain": "systematic_trading",
        "title": "交易系統規範：憲法+風控+策略分類+海龜",
        "key_concepts": [
            "三大交易憲法：損失控制（嚴格停損）、部位控制（風險承受度）、情緒控制（失控強制離場）",
            "風險限額：日MDD<=3%總資金；單筆MDD<=1%~1.5%；日最大5筆，50口大台",
            "部位架構：菱形加碼[2,3,3,2]；母單(Trend)30%/趨勢單(Pullback)40%/動能單(Momentum)30%",
            "順勢單賺賠比>=1:3；逆勢單賺賠比1:1.1~1.2（靠高勝率>51%獲利）",
            "海龜系統：N=20日EMA TR；Unit=1%帳戶淨值/(N*Dollar/point)",
            "海龜進場：System1突破20日高點（上次虧損才執行）；System2突破55日高點",
            "海龜加碼：每0.5N加1Unit，最多4Unit；停損2N；出場S1跌破10日低/S2跌破20日低",
            "策略命名：!!Prod/!@Beta/!Dev + 商品_時段_波段當沖_週期_策略名",
            "Walk-Forward Analysis：確保OOS獲利能力；ATR加權資金管理：r*N*ATR+(1-r)*Const"
        ],
        "summary": "完整交易系統規範。三法則：損失控制、部位控制、情緒控制。日MDD上限3%，單筆1-1.5%。海龜法則完整實作：ATR定位、20/55日突破進場、0.5N加碼、2N停損、10/20日低出場。WF分析+ATR加權資金管理。"
    },
    {
        "source_file": "E:/投資交易/量化金融文獻/交易系統完整結構.md",
        "source_tag": "tier1_md",
        "timestamp": now,
        "domain": "systematic_trading",
        "title": "交易系統完整結構：供需失衡框架+ATR+Z-Score+績效診斷",
        "key_concepts": [
            "交易本質：EV=P_w*V_w - P_l*V_l > 0且>總成本(手續費+稅)",
            "供需失衡策略：數據驗證/籌碼清洗（融資維持率<130%）/產業結構/資訊速度差",
            "ATR標準化：ATR_norm=ATR/Close*100，跨標的比較波動",
            "Entropy信號過濾：H=-sum(p_i*log2(p_i))；H>0.7縮倉觀望；H<0.3放大順勢",
            "MAE公式：MAE_i=min(P_t-P_entry)；MFE_i=max(P_t-P_entry)；自適化SL/TP用中位數*ATR_norm",
            "Z-Score策略：Z=(X-mu)/sigma；Z>+2逆勢建空；-2~+2趨勢跟隨；Z<-2逆勢建多",
            "績效診斷：Expectancy>0；Profit Factor 1.5~2.5；Recovery Factor越高越好；Sharpe>1.0",
            "0050風險：台積電>50%，R_tw約等於R_tsmc，不具分散效果",
            "宏觀AI算力：短期Bloom Energy(燃料電池)/中期Oklo(SMR)/長期Helion(核融合)"
        ],
        "summary": "完整交易系統架構。EV>0是核心。ATR標準化、Entropy雜訊過濾、Z-Score均值回歸、MAE/MFE自適應停損。四大績效指標健康值。AI算力宏觀布局三階段。0050不等於分散（台積電占比>50%）。"
    },
    {
        "source_file": "E:/投資交易/量化金融文獻/投資管理與資金控管_筆記.md",
        "source_tag": "tier1_md",
        "timestamp": now,
        "domain": "money_management",
        "title": "資金控管模型：Kelly + VaR + MDD + 預測心法",
        "key_concepts": [
            "Kelly公式：f=(b*p-q)/b；b=賠率(Win/Loss)；p=勝率；EV<=0不下注",
            "半凱利(Half-Kelly)：實務使用1/2~1/3 Kelly，降低波動風險",
            "平賭法(Martingale)：絕對不可用，破產風險無限大",
            "反平賭法(Anti-Martingale)：贏加碼輸減碼，符合截斷虧損讓利潤奔跑",
            "金字塔加碼：加碼部位<原始部位，避免頭重腳輕",
            "VaR：95%或99%信心水準下的最大可能損失；無法捕捉肥尾/極端事件",
            "MDD：恢復指數級（跌50%需漲100%回本）",
            "2%法則：單筆風險<=總資金2%；部位股數=總資金*2%/(進場價-停損價)",
            "預測：狐狸(多視角彈性調整)>刺蝟(單一大觀點)；貝氏更新；集體智慧"
        ],
        "summary": "資金管理三大工具：Kelly公式（最優複利下注）、VaR（風險量化限制）、2%法則（單筆風險上限）。絕不用Martingale。Anti-Martingale+金字塔加碼符合趨勢交易原則。預測心法：貝氏更新+狐狸多視角。"
    },
    {
        "source_file": "E:/投資交易/量化金融文獻/資產配置系統.md",
        "source_tag": "tier1_md",
        "timestamp": now,
        "domain": "asset_allocation",
        "title": "資產配置系統：下方風險最小化+核心衛星架構",
        "key_concepts": [
            "目標函數：Maximize U=E[R_p]-lambda*Risk_downside；約束：Real Return>=0，MaxDD<=20~25%，流動性>=6個月生活費",
            "Semi-Deviation=sqrt(sum(min(R_i-MAR,0)^2)/N)；MAR=通膨+2%",
            "資產角色：QQQ(成長)/BTC(凸性放大,sigma>60%)/GLD(回撤吸收)/XLV.XLP(防禦)/USMV.SPLV(波動壓縮)",
            "核心60%：USMV20%/XLV.XLP15%/GLD15%/TLT.IEI10%",
            "衛星40%：QQQ30%/TQQQ5%/BTC5%",
            "四象限通膨矩陣：低通膨高成長→QQQ；高通膨高成長→原物料房地產；低通膨衰退→TLT；高通膨衰退→GLD.TIPS.BTC",
            "全天候：VT30%/TLT35%/IEI15%/GLD7.5%/DBC7.5%/BTC5%",
            "再平衡：每季時間觸發+偏離5%強制觸發",
            "壓力測試：2008 -18%(vs QQQ-50%)；2020 -12%(vs-30%)；2022 -15%(vs-33%)"
        ],
        "summary": "資產配置系統設計。目標：最小化下方風險，MaxDD上限25%，實質報酬>=0。核心衛星架構：60%防禦(USMV/GLD/債)+40%進攻(QQQ/BTC)。四象限通膨矩陣指導戰術配置。歷史壓力測試均顯著優於純QQQ。"
    },
    {
        "source_file": "E:/投資交易/參考書籍/Natenberg_期權波動率與定價_筆記.md",
        "source_tag": "tier1_md",
        "timestamp": now,
        "domain": "derivatives_options",
        "title": "Natenberg選擇權波動率與定價：遠期合約定價、結算機制、套利",
        "key_concepts": [
            "遠期合約公式：F=現貨*(1+r*t)+儲存費-便利收益；商品市場contango vs backwardation",
            "股票遠期：F=[S*(1+r*t)]-D（D為預期股息）；可推算implied spot/rate/dividend",
            "基差=現貨-遠期；通常為負（成本>便利收益）；便利收益高時可正",
            "Stock-type settlement（選擇權）vs Futures-type settlement（期貨：margin+daily variation）",
            "套利：現貨-期貨差距超過成本→cash-and-carry套利；放空股票的short rebate影響套利邊界",
            "保證金(margin)屬交易者可賺利息；variation是P&L移轉",
            "交換所(clearinghouse)：買賣雙方中介，保障違約，美國無clearinghouse破產案例",
            "北美選擇權用stock-type settlement，期貨用futures-type；混用可能造成現金流問題"
        ],
        "summary": "Natenberg選擇權波動率定價教材精華。遠期定價：現貨+資金成本-便利收益。股票遠期F=[S(1+rt)]-D。Implied值反推法。Stock vs Futures結算差異。套利邊界由借券成本決定。Clearinghouse保障市場完整性。"
    },
    {
        "source_file": "E:/投資交易/參考書籍/MAFE_起源與理論.md",
        "source_tag": "tier1_md",
        "timestamp": now,
        "domain": "strategy_optimization",
        "title": "MAE/MFE起源：資金管理歷史脈絡+隨機波動理論",
        "key_concepts": [
            "資金管理兩大問題：(1)正EV賭博如何最大化；(2)運氣不佳時停損點控制",
            "發展脈絡：1956 Shannon資訊熵→Kelly公式→1969 Thorp(21點)→1990理論成熟→2000另類投資基石",
            "停損研究：Shefrin&Statman1985處置效應→席尼1985停損位置→海龜1983-1995→Vince1995新資金管理",
            "MAE MFE專書：1997 John Sweeney出版；海龜法則中有相關概念",
            "隨機波動理論：金融資料特徵=leptokurtic(高狹峰)+fat tail(厚尾)+volatility clustering",
            "1970時變波動率→1980選擇權修正→1990市場驗證→2000高低變幅&市場模擬",
            "量化迷思：預測需考慮交易成本(手續費+價差+滑價+隔夜利息)；ML不優於ARIMA；過擬合根本是樣本代表性",
            "分析單位：非方向性風險(波動幅度)比方向性風險(漲跌方向)更容易計算"
        ],
        "summary": "MAE/MFE理論起源。資金管理發展：Shannon→Kelly→Thorp→海龜→Vince，1997年席尼正式出版MAE專書。金融資料統計特徵：厚尾+高狹峰+波動叢聚，不符合常態分布。ML預測不優於ARIMA，overfitting根本問題在樣本代表性。"
    },
    {
        "source_file": "E:/投資交易/量化金融文獻/賽局博弈系統完整整理.md",
        "source_tag": "tier1_md",
        "timestamp": now,
        "domain": "decision_theory",
        "title": "賽局博弈系統：阿瓦隆為核心的決策推理框架",
        "key_concepts": [
            "五大邏輯公理：一致性/廣泛性/精簡性(奧卡姆剃刀)/優勢性(dominant strategy)/可證偽性",
            "決策原則：排除優於指認（先確認好人，壞人搜索範圍自然縮小）",
            "動態修正：Bayesian Updating，每輪投票=新數據D，更新P(H|D)",
            "勝利公式：Victory=Logic*Trust + Deception*Chaos",
            "壞人深水狼策略：前期模仿好人，最後一局背刺；混亂製造降低信息處理效率",
            "延伸應用：金融市場對手盤識別/商務談判意圖偵測/組織政治派系識別",
            "評估標準：非輸贏，而是每個決策點是否基於當下資訊做出最優解"
        ],
        "summary": "以阿瓦隆為核心模型的決策推理系統，可直接應用於交易對手盤識別。五大邏輯公理：一致性、廣泛性、奧卡姆、優勢策略、可證偽性。核心：排除>指認，Bayesian動態更新。評估標準是決策品質非結果。"
    },
    {
        "source_file": "E:/投資交易/量化金融文獻/量化選股_專利與預測_筆記.md",
        "source_tag": "tier1_md",
        "timestamp": now,
        "domain": "quant_investing",
        "title": "量化選股：專利大數據預測股價",
        "key_concepts": [
            "核心假設：專利→產品→財報（領先關係），專利是財報的領先指標",
            "三大專利指標：數量（研發投入/技術屏障）/趨勢（申請量增減反映產業熱度）/品質（引用次數/專利家族大小）",
            "案例(2012-2015台股)：鴻海、聯詠、台達電、大立光；專利選股勝率60%~100%，優於大盤",
            "另類數據三類：財報(落後)→對比→專利/供應鏈/網路流量(領先)",
            "護城河識別：持續高質量專利產出=技術型公司護城河"
        ],
        "summary": "專利大數據量化選股。核心邏輯：專利申請量趨勢領先營收財報。台股實證：專利篩選組合(鴻海/聯詠/台達電/大立光)2012-2015勝率60-100%。另類數據(專利/供應鏈/流量)比財報更有前瞻性。"
    },
    {
        "source_file": "E:/投資交易/量化金融文獻/股票量化分析架構流程.md",
        "source_tag": "tier1_md",
        "timestamp": now,
        "domain": "quant_investing",
        "title": "股票量化分析ML建模10步驟流程",
        "key_concepts": [
            "10步驟：目標設定→數據蒐集→模型選擇→標記目標→整理特徵→訓練/驗證/測試三切分→學習→調整→測驗→績效分析→保留/重建",
            "三集分割：訓練集(學習)、驗證集(調整)、測試集(模擬未知)",
            "決策閾值：模型保留→實際應用；不保留→重新建設"
        ],
        "summary": "機器學習預測股價的10步驟框架。核心是三集分割（訓練/驗證/測試）和績效分析驅動的模型保留決策。"
    }
]

output_path = "C:/Users/admin/workspace/digital-immortality/results/digestion_log.jsonl"
count = 0
with open(output_path, "a", encoding="utf-8") as f:
    for entry in entries:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        count += 1

print(f"Written {count} entries to digestion_log.jsonl")

# Update digested_set.txt
digested_path = "C:/Users/admin/workspace/digital-immortality/results/digested_set.txt"
with open(digested_path, "a", encoding="utf-8") as f:
    for entry in entries:
        f.write(entry["source_file"] + "\n")

print(f"Updated digested_set.txt with {count} entries")
