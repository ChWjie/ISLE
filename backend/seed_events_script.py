
import requests
import json
import random
from datetime import datetime, timedelta

API_URL = "http://localhost:8000/api/v1/events"

def random_date(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds())),
    )

start_date = datetime(2025, 1, 1)
end_date = datetime(2026, 4, 1)

events_data = [
    {
        "name": "某互联网公司违规收集用户个人信息案",
        "description": "深圳某互联网公司在未明确告知用户的情况下，违规收集用户位置、通讯录等敏感个人信息，被监管部门立案调查。",
        "dispute_type": "数据安全合规",
        "our_side": ["企业法务部", "合规委员会"],
        "opponent_side": ["国家互联网信息办公室", "用户维权代表"],
        "legal_systems": ["《个人信息保护法》", "《网络安全法》", "《数据安全法》"],
        "fact_summary": "企业APP在用户未明确同意情况下调用位置权限，并将数据共享给第三方广告平台，监管部门依据《个人信息保护法》第17条启动执法程序。",
        "opponent_stance_preset": "监管部门主张企业违反了告知同意原则，收集超出业务必要范围，应依法承担行政责任并整改。",
        "opponent_claims_options": ["违反最小必要原则", "未履行告知义务", "非法向第三方提供个人信息", "未建立个人信息保护管理制度"],
        "opponent_legal_system": "cn_data_law"
    },
    {
        "name": "制造企业拖欠农民工工资劳动仲裁案",
        "description": "广州某制造企业因资金周转困难，拖欠200余名农民工约380万元工资，劳动者集体申请劳动仲裁。",
        "dispute_type": "劳动合规",
        "our_side": ["企业法务部", "人力资源部"],
        "opponent_side": ["劳动仲裁委员会", "农民工代表团"],
        "legal_systems": ["《劳动合同法》", "《工资支付暂行规定》", "《保障农民工工资支付条例》"],
        "fact_summary": "企业因订单下滑资金紧张，连续3个月未足额发放工资。劳动者向仲裁委提出仲裁申请，要求支付拖欠工资及经济补偿金。",
        "opponent_stance_preset": "劳动者主张依据《劳动合同法》第85条，要求企业按应付金额50%-100%加付赔偿金，并追究企业负责人法律责任。",
        "opponent_claims_options": ["拖欠工资违法", "要求加付赔偿金", "申请先予执行", "追究刑事责任"],
        "opponent_legal_system": "cn_labor_law"
    },
    {
        "name": "电商平台二选一不正当竞争纠纷",
        "description": "某头部电商平台要求入驻商家签署独家合作协议，禁止商家同时在竞争平台销售，引发反垄断调查。",
        "dispute_type": "竞争合规",
        "our_side": ["企业法务部", "外部律所"],
        "opponent_side": ["国家市场监督管理总局", "受损商家联合会"],
        "legal_systems": ["《反垄断法》", "《反不正当竞争法》", "《电子商务法》"],
        "fact_summary": "监管部门认定该平台滥用市场支配地位，强迫经营者进行二选一，违反《反垄断法》第22条，启动行政处罚程序。",
        "opponent_stance_preset": "监管方认为企业具有市场支配地位，其独家合作要求构成滥用市场支配地位行为，应依法处以营业额1%-10%的罚款。",
        "opponent_claims_options": ["滥用市场支配地位", "限制市场竞争", "损害商家利益", "违反公平竞争原则"],
        "opponent_legal_system": "cn_competition_law"
    },
    {
        "name": "软件公司商业秘密泄露侵权案",
        "description": "北京某软件公司前核心技术员工离职后加入竞争对手，并将原公司核心算法及客户数据带走使用，原公司提起诉讼。",
        "dispute_type": "知识产权",
        "our_side": ["原告企业法务部", "知识产权律所"],
        "opponent_side": ["被告前员工", "竞争对手公司"],
        "legal_systems": ["《反不正当竞争法》", "《劳动合同法》", "《刑法》第219条"],
        "fact_summary": "被告离职前通过公司内网下载大量源代码及客户数据库，入职新公司后用于同类产品开发。原告申请证据保全并提起诉讼，索赔500万元。",
        "opponent_stance_preset": "被告主张涉案技术属于个人技能积累，客户信息系合法获取，不构成侵犯商业秘密，请求驳回原告全部诉求。",
        "opponent_claims_options": ["否认商业秘密性质", "主张个人技能积累", "技术公知域抗辩", "无损害结果抗辩"],
        "opponent_legal_system": "cn_ip_law"
    },
    {
        "name": "建筑企业挂靠承包合同纠纷",
        "description": "上海某建筑公司以挂靠方式承接工程项目，工程质量不合格引发业主索赔，被挂靠单位与实际施工方责任划分产生争议。",
        "dispute_type": "合同纠纷",
        "our_side": ["被挂靠建筑公司法务部"],
        "opponent_side": ["业主方", "实际施工团队"],
        "legal_systems": ["《建筑法》", "《合同法》", "《建设工程施工合同司法解释》"],
        "fact_summary": "实际施工人以被挂靠企业名义签订合同，工程完工后出现重大质量问题，业主要求连带赔偿2000万元，被挂靠企业与实际施工方互相推脱责任。",
        "opponent_stance_preset": "业主方主张被挂靠企业与实际施工人应承担连带责任，要求二者共同承担质量损失赔偿及工期违约金。",
        "opponent_claims_options": ["连带责任主张", "合同无效抗辩", "工程质量鉴定申请", "索赔施工损失"],
        "opponent_legal_system": "cn_civil_law"
    },
    {
        "name": "上市公司信息披露违规证券处罚案",
        "description": "杭州某上市公司在年报中虚增营业收入约3亿元，隐瞒重大关联交易，证监会立案调查并拟处以行政处罚。",
        "dispute_type": "证券合规",
        "our_side": ["上市公司法务部", "独立董事"],
        "opponent_side": ["中国证券监督管理委员会", "投资者保护机构"],
        "legal_systems": ["《证券法》", "《上市公司信息披露管理办法》", "《刑法》第160条"],
        "fact_summary": "证监会调查发现，公司通过虚构销售合同虚增收入，并未在年报中如实披露控股股东占用资金情况，导致股价异常波动，众多投资者受损。",
        "opponent_stance_preset": "证监会认定公司存在信息披露虚假陈述，拟对公司处以顶格罚款1000万元，并对相关责任人采取市场禁入措施。",
        "opponent_claims_options": ["虚假陈述违法", "要求高管承担连带责任", "投资者损失赔偿请求", "撤销相关股权激励"],
        "opponent_legal_system": "cn_securities_law"
    },
    {
        "name": "食品企业产品质量安全违规案",
        "description": "成都某食品公司生产的产品被检测出食品添加剂超标，多名消费者投诉后市场监管部门介入检查，企业面临召回和处罚。",
        "dispute_type": "合规监管",
        "our_side": ["企业法务部", "质量管理部"],
        "opponent_side": ["市场监督管理局", "消费者协会"],
        "legal_systems": ["《食品安全法》", "《产品质量法》", "《消费者权益保护法》"],
        "fact_summary": "抽样检测发现企业旗下零食产品中防腐剂苯甲酸钠含量超国家标准2.3倍，监管部门依法要求停产整改、召回全部问题产品，消费者提出索赔诉求。",
        "opponent_stance_preset": "监管部门依据《食品安全法》第124条，主张对企业处以货值金额5-10倍罚款，吊销食品生产许可证，并追究相关负责人责任。",
        "opponent_claims_options": ["产品质量不合格", "要求停产召回", "行政处罚依据", "消费者赔偿请求"],
        "opponent_legal_system": "cn_food_law"
    },
    {
        "name": "科技公司员工竞业限制协议纠纷",
        "description": "武汉某科技公司前高管离职后3个月即加入同行业竞争公司，原公司依据竞业限制协议申请劳动仲裁要求支付违约金。",
        "dispute_type": "劳动合规",
        "our_side": ["原告企业法务部"],
        "opponent_side": ["前高管", "竞争对手公司"],
        "legal_systems": ["《劳动合同法》第23-24条", "《劳动争议调解仲裁法》"],
        "fact_summary": "离职前高管签署了为期2年、月补偿金5000元的竞业限制协议，离职后仅3个月加入竞争对手，原公司依据协议主张违约金30万元。",
        "opponent_stance_preset": "前高管主张竞业限制范围过宽，补偿金标准过低不具约束力，且新公司业务与原公司不存在实质竞争关系，请求认定协议无效。",
        "opponent_claims_options": ["限制范围过宽抗辩", "补偿金不足抗辩", "非竞争业务抗辩", "协议无效主张"],
        "opponent_legal_system": "cn_labor_law"
    },
    {
        "name": "房地产公司违规预售商品房案",
        "description": "南京某房地产公司在未取得预售许可证的情况下，通过"认筹"方式变相收取购房款约1.2亿元，被住建部门查处。",
        "dispute_type": "合规监管",
        "our_side": ["房产公司法务部"],
        "opponent_side": ["住房和城乡建设局", "购房者代表"],
        "legal_systems": ["《城市商品房预售管理办法》", "《房地产管理法》", "《合同法》"],
        "fact_summary": "该公司以"内部认筹"名义向500余名购房者收取定金，但实际未办理预售许可，购房者要求退款并支付利息损失，监管部门予以行政处罚。",
        "opponent_stance_preset": "购房者主张合同无效，要求退还全部款项并按银行贷款利率赔偿资金占用损失；监管部门处以5倍以下罚款。",
        "opponent_claims_options": ["违规预售违法", "合同无效请求", "退款及利息赔偿", "行政罚款处罚"],
        "opponent_legal_system": "cn_civil_law"
    },
    {
        "name": "跨国企业跨境数据传输合规审查案",
        "description": "某跨国公司将中国用户数据传输至境外服务器处理，未按规定进行数据出境安全评估，被网信部门责令整改。",
        "dispute_type": "数据安全合规",
        "our_side": ["企业数据合规部", "外部专项律所"],
        "opponent_side": ["国家互联网信息办公室", "地方网信办"],
        "legal_systems": ["《数据安全法》", "《个人信息保护法》", "《数据出境安全评估办法》"],
        "fact_summary": "该公司将超过100万条中国用户个人信息及重要数据传输至美国总部服务器，未事先向网信办申报数据出境安全评估，被发现后面临整改和罚款。",
        "opponent_stance_preset": "网信部门认定企业违反数据本地化要求及数据出境管理规定，责令限期整改，并依法处以100万以上罚款，情节严重可暂停数据处理活动。",
        "opponent_claims_options": ["违反数据出境规定", "未履行安全评估义务", "数据本地化要求", "责令整改停止违规"],
        "opponent_legal_system": "cn_data_law"
    },
    {
        "name": "医药企业商业贿赂合规调查案",
        "description": "重庆某医药公司被举报通过讲课费、学术会议等方式向医生行贿，以推广处方药，国家卫健委及市场监管局联合调查。",
        "dispute_type": "合规监管",
        "our_side": ["企业合规部", "法务部"],
        "opponent_side": ["国家卫生健康委员会", "市场监督管理局"],
        "legal_systems": ["《反不正当竞争法》", "《药品管理法》", "《刑法》第163条"],
        "fact_summary": "调查发现该公司2020-2025年间累计向200余名医生支付超过1500万元的不正当利益，通过药品销量提成、虚假学术会议等方式进行商业贿赂。",
        "opponent_stance_preset": "监管部门认定企业行为构成商业贿赂，违反《反不正当竞争法》第7条，拟处以违法所得1-3倍罚款，并将相关责任人移送司法机关。",
        "opponent_claims_options": ["商业贿赂违法认定", "没收违法所得", "行政罚款处罚", "刑事责任追究"],
        "opponent_legal_system": "cn_competition_law"
    },
    {
        "name": "物流公司劳务外包员工工伤认定纠纷",
        "description": "广州某物流公司快递员在配送途中发生交通事故受伤，因劳务外包关系复杂，工伤认定及赔偿责任归属产生争议。",
        "dispute_type": "劳动合规",
        "our_side": ["物流公司法务部"],
        "opponent_side": ["受伤快递员", "劳动保障行政部门"],
        "legal_systems": ["《工伤保险条例》", "《劳动合同法》", "《最高人民法院关于审理工伤保险行政案件若干问题的规定》"],
        "fact_summary": "受伤快递员与劳务派遣公司签订合同，实际在物流公司平台工作。工伤认定机构认定工伤后，用工单位、派遣公司、平台三方对赔偿责任互相推诿，劳动者维权困难。",
        "opponent_stance_preset": "劳动者主张实际用工的物流平台公司应承担工伤赔偿连带责任，不应因外包形式规避雇主法律义务。",
        "opponent_claims_options": ["认定劳动关系", "要求连带赔偿", "工伤医疗费用承担", "停工留薪期工资请求"],
        "opponent_legal_system": "cn_labor_law"
    },
    {
        "name": "网络平台算法歧视消费者权益案",
        "description": "某外卖平台被曝光对新老用户实施差异化定价，老用户反而比新用户支付更高配送费，引发消费者投诉和监管关注。",
        "dispute_type": "合规监管",
        "our_side": ["平台法务部", "算法合规团队"],
        "opponent_side": ["消费者权益保护委员会", "市场监督管理局"],
        "legal_systems": ["《消费者权益保护法》", "《互联网信息服务算法推荐管理规定》", "《价格法》"],
        "fact_summary": "平台通过用户画像对消费能力强的老用户实施价格歧视，相同订单老用户配送费高出新用户30%-50%，消费者协会收到大量投诉后向监管部门举报。",
        "opponent_stance_preset": "监管部门认定平台价格歧视行为违反公平交易原则，损害消费者合法权益，要求整改并处以相应行政处罚，同时责令公开算法规则。",
        "opponent_claims_options": ["价格歧视违法", "算法透明度要求", "消费者损失赔偿", "整改算法推荐规则"],
        "opponent_legal_system": "cn_consumer_law"
    },
]

def seed_events():
    print("开始写入企业合规案件数据...")
    count = 0
    for evt in events_data:
        payload = {
            "event_id": f"evt-{random.randint(10000, 99999)}",
            "name": evt["name"],
            "description": evt["description"],
            "dispute_type": evt["dispute_type"],
            "our_side": evt["our_side"],
            "opponent_side": evt["opponent_side"],
            "legal_systems": evt["legal_systems"],
            "fact_summary": evt["fact_summary"],
            "opponent_stance_preset": evt.get("opponent_stance_preset"),
            "opponent_claims_options": evt.get("opponent_claims_options", []),
            "opponent_legal_system": evt.get("opponent_legal_system")
        }

        try:
            resp = requests.post(API_URL, json=payload)
            if resp.status_code == 200:
                print(f"✓ 已创建: {evt['name']}")
                count += 1
            else:
                print(f"✗ 失败 {evt['name']}: {resp.text}")
        except Exception as e:
            print(f"✗ 连接错误 {evt['name']}: {e}")

    print(f"\n写入完成，共创建 {count} 条案件。")

if __name__ == "__main__":
    seed_events()
