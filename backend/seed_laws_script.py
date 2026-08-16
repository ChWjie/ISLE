import sys
import os
from datetime import datetime

# Add current directory to path so we can import app modules
sys.path.append(os.getcwd())

from app.database import SessionLocal, engine
from app.models.database import Base, Law

# Drop existing table to ensure schema update
Law.__table__.drop(engine, checkfirst=True)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def seed_laws():
    db = SessionLocal()

    # 1. Clear existing laws? Maybe not, just add if not exists.
    # For this script we'll check existence by code.

    laws_data = [
        # --- UNCLOS (United Nations Convention on the Law of the Sea) ---
        {
            "code": "UNCLOS-56",
            "name_zh": "联合国海洋法公约第56条 - 沿海国在专属经济区的权利、管辖权和义务",
            "category": "海洋法",
            "level": "国际公约",
            "region": "UN",
            "content": """
1. 沿海国在专属经济区内有：
(a) 以勘探和开发、养护和管理海床上覆水域和海床及其底土的自然资源（不论为生物或非生物资源）为目的的主权权利，以及关于在该区内从事经济性开发和勘探，如利用海水、海流和风力生产能等其他活动的主权权利；
(b) 本公约有关条款规定的对下列事项的管辖权：
(i) 人工岛屿、设施和结构的建造和使用；
(ii) 海洋科学研究；
(iii) 海洋环境的保护和保全；
(c) 本公约规定的其他权利和义务。
2. 沿海国在专属经济区内根据本公约行使其权利和履行其义务时，应适当顾及其他国家的权利和义务，并应以符合本公约规定的方式行事。
3. 本条所载的权利，关于海床和底土，应按照第六部分的规定行使。
            """,
            "summary": "规定了沿海国在专属经济区的主权权利（资源开发）和管辖权（人工岛、科研、环保）。",
            "effective_date": datetime(1994, 11, 16)
        },
        {
            "code": "UNCLOS-58",
            "name_zh": "联合国海洋法公约第58条 - 其他国家在专属经济区的权利和义务",
            "category": "海洋法",
            "level": "国际公约",
            "region": "UN",
            "content": """
1. 在专属经济区内，所有国家，不论为沿海国或内陆国，在公约有关规定的限制下，享有第八十七条所指的航行和飞越的自由，铺设海底电缆和管道的自由，以及与这些自由有关的海洋其他国际合法用途，诸如与船舶和飞机的操作及海底电缆和管道的使用有关的并符合本公约其他规定的用途。
2. 第八十八至第一一五条以及其他国际法有关规则，只要与本部分不相抵触，均适用于专属经济区。
3. 国家在专属经济区内根据本公约行使其权利和履行其义务时，应适当顾及沿海国的权利和义务，并应遵守沿海国按照本公约的规定和其他国际法规则所制定的与本部分不相抵触的法律和规章。
            """,
            "summary": "保障了所有国家在专属经济区的航行、飞越和铺设电缆管道的自由。",
            "effective_date": datetime(1994, 11, 16)
        },
        {
            "code": "UNCLOS-74",
            "name_zh": "联合国海洋法公约第74条 - 海岸相向或相邻国家间专属经济区界限的划定",
            "category": "海洋法",
            "level": "国际公约",
            "region": "UN",
            "content": """
1. 海岸相向或相邻国家间专属经济区界限的划定，应在国际法院规约第三十八条所指国际法的基础上以协议划定，以便得到公平解决。
2. 有关国家如在合理期间内未能达成任何协议，应诉诸第十五部分所规定的程序。
3. 在达成第一款规定的协议以前，有些国家应基于谅解和合作的精神，尽一切努力作出实际性的临时安排，并在此过渡期间内，不危害或阻碍最后协议的达成。这种安排应不妨碍最后界限的划定。
4. 如存在现行有效的协定，专属经济区界限的划定，应按照该协定的规定决定。
            """,
            "summary": "规定了专属经济区划界应遵循公平原则，并鼓励临时安排。",
            "effective_date": datetime(1994, 11, 16)
        },
        {
            "code": "UNCLOS-121",
            "name_zh": "联合国海洋法公约第121条 - 岛屿制度",
            "category": "海洋法",
            "level": "国际公约",
            "region": "UN",
            "content": """
1. 岛屿是四面环水并在高潮时高于水面的自然形成的陆地。
2. 除第三款规定外，岛屿的领海、毗连区、专属经济区和大陆架应按照本公约适用于其他陆地领土的规定加以划定。
3. 不能维持人类居住或其本身的经济生活的岩礁，不应有专属经济区或大陆架。
            """,
            "summary": "定义了岛屿，并规定岩礁不享有专属经济区或大陆架，这是南海仲裁案的核心争议条款。",
            "effective_date": datetime(1994, 11, 16)
        },
        {
            "code": "UNCLOS-298",
            "name_zh": "联合国海洋法公约第298条 - 适用第二节具拘束力的裁判程序的任择性例外",
            "category": "海洋法",
            "level": "国际公约",
            "region": "UN",
            "content": """
1. 一国在签署、批准或加入本公约时，或在其后任何时间，在不妨害第一款所定义务的情形下，可以书面声明对于下列各类争端的一类或一类以上，不接受第二节规定的一种或一种以上的程序：
(a) (i) 关于划定海洋边界的争端，或涉及历史性海湾或所有权的争端...
(b) 关于军事活动，包括从事非商业服务的政府船只和飞机的军事活动的争端...
(c) 正在联合国安全理事会执行《联合国宪章》所赋予的职务的争端...
            """,
            "summary": "赋予缔约国权利，可声明排除海洋划界、军事活动等争端适用强制仲裁程序。中国已于2006年根据此条作出排除性声明。",
            "effective_date": datetime(1994, 11, 16)
        },

        # --- PRC Laws ---
        {
            "code": "CCG-22",
            "name_zh": "中华人民共和国海警法第22条 - 采取必要措施（包括使用武器）的权力",
            "category": "国内法",
            "level": "法律",
            "region": "CN",
            "content": """
国家主权、主权权利和管辖权在海上正在受到外国组织和个人的不法侵害或者面临不法侵害的紧迫危险时，海警机构有权依照本法和其他相关法律、行政法规，采取包括使用武器在内的一切必要措施制止侵害、排除危险。
            """,
            "summary": "授权海警在国家主权受侵害时使用武器。",
            "effective_date": datetime(2021, 2, 1)
        },
        {
            "code": "CCG-25",
            "name_zh": "中华人民共和国海警法第25条 - 临时海上警戒区",
            "category": "国内法",
            "level": "法律",
            "region": "CN",
            "content": """
有下列情形之一的，省级以上海警局可以划定临时海上警戒区，限制或者禁止船舶、人员通行、停留，并予以公告：
(一) 执行海上安全保卫任务需要的；
(二) 查缉海上严重犯罪案件需要的；
(三) 应对海上突发事件需要的；
(四) 保护海洋资源和生态环境需要的；
(五) 法律、行政法规规定的其他情形。
            """,
            "summary": "授权海警划定临时警戒区，限制通行。",
            "effective_date": datetime(2021, 2, 1)
        },
         {
            "code": "PRC-EEZ-14",
            "name_zh": "中华人民共和国专属经济区和大陆架法第14条 - 维护权益措施",
            "category": "国内法",
            "level": "法律",
            "region": "CN",
            "content": """
中华人民共和国主管机关有权对违反中华人民共和国法律、法规的外国船舶进行紧追、监视、登临、检查、扣押、逮捕和司法程序，并行使处罚权。
            """,
            "summary": "规定了在专属经济区执法的具体权力。",
            "effective_date": datetime(1998, 6, 26)
        },

        # --- Customary International Law / Guidelines ---
        {
            "code": "CIL-FON",
            "name_zh": "国际习惯法 - 航行自由 (Freedom of Navigation)",
            "category": "国际惯例",
            "level": "习惯法",
            "region": "INT",
            "content": """
航行自由是习惯国际法的一项基本原则，指除国际法规定的例外情况外，挂有任何主权国家旗帜的船舶不受其他国家干扰地航行的权利。此权利既适用于公海，也在一定限制下适用于专属经济区和领海（无害通过）。
            """,
            "summary": "国际法基本原则，保障公海航行自由。",
            "effective_date": datetime(1609, 1, 1) # Hugo Grotius Mare Liberum roughly
        },
        {
            "code": "DOC-2002",
            "name_zh": "南海各方行为宣言 (DOC)",
            "category": "国际法",
            "level": "政治宣言",
            "region": "ASEAN-CN",
            "content": """
...各方承诺保持自我克制，不采取使争议复杂化、扩大化和影响和平与稳定的行动，包括不在现无人居住的岛、礁、滩、沙或其它自然构造上采取居住的行动，并以建设性的方式处理它们的分歧。
            """,
            "summary": "中国与东盟国家签署的政治文件，承诺自我克制。",
            "effective_date": datetime(2002, 11, 4)
        },

        # --- PRC Territorial Sea and Contiguous Zone Law ---
        {
            "code": "PRC-TSCZ-2",
            "name_zh": "中华人民共和国领海及毗连区法第2条 - 领海范围",
            "category": "国内法",
            "level": "法律",
            "region": "CN",
            "content": """
中华人民共和国领海为邻接中华人民共和国陆地领土和内水的一带海域。
中华人民共和国的陆地领土包括中华人民共和国大陆及其沿海岛屿、台湾及其包括钓鱼岛在内的附属各岛、澎湖列岛、东沙群岛、西沙群岛、中沙群岛、南沙群岛以及其他一切属于中华人民共和国的岛屿。
中华人民共和国领海基线向陆地一侧的水域为中华人民共和国的内水。
            """,
            "summary": "明确了中国的陆地领土范围，包括台湾、钓鱼岛及南海诸岛。",
            "effective_date": datetime(1992, 2, 25)
        },
        {
            "code": "PRC-TSCZ-3",
            "name_zh": "中华人民共和国领海及毗连区法第3条 - 领海宽度",
            "category": "国内法",
            "level": "法律",
            "region": "CN",
            "content": """
中华人民共和国领海的宽度从领海基线量起为十二海里。
中华人民共和国领海基线采用直线基线法划定，由各相邻基点之间的直线连线组成。
中华人民共和国领海的外部界限为一条其每一点与领海基线的最近点距离等于十二海里的线。
            """,
            "summary": "确立了12海里领海宽度及直线基线法。",
            "effective_date": datetime(1992, 2, 25)
        },
        {
            "code": "PRC-TSCZ-4",
            "name_zh": "中华人民共和国领海及毗连区法第4条 - 毗连区",
            "category": "国内法",
            "level": "法律",
            "region": "CN",
            "content": """
中华人民共和国毗连区为领海以外邻接领海的一带海域。毗连区的宽度为十二海里。
中华人民共和国毗连区的外部界限为一条其每一点与领海基线的最近点距离等于二十四海里的线。
            """,
            "summary": "确立了毗连区范围为领海以外12海里。",
            "effective_date": datetime(1992, 2, 25)
        },
        {
            "code": "PRC-TSCZ-6",
            "name_zh": "中华人民共和国领海及毗连区法第6条 - 无害通过与军舰批准",
            "category": "国内法",
            "level": "法律",
            "region": "CN",
            "content": """
外国非军用船舶，享有依法无害通过中华人民共和国领海的权利。
外国军用船舶进入中华人民共和国领海，须经中华人民共和国政府批准。
            """,
            "summary": "规定外军舰船进入中国领海须经批准（区别于无害通过）。",
            "effective_date": datetime(1992, 2, 25)
        },

        # --- PRC Anti-Foreign Sanctions Law ---
        {
            "code": "PRC-AFS-3",
            "name_zh": "中华人民共和国反外国制裁法第3条 - 反对干涉内政",
            "category": "国内法",
            "level": "法律",
            "region": "CN",
            "content": """
中华人民共和国反对霸权主义和强权政治，反对任何国家以任何借口、任何方式干涉中国内政。
外国国家违反国际法和国际关系基本准则，以各种借口或者依据其本国法律对我国进行遏制、打压，对我国公民、组织采取歧视性限制措施，干涉我国内政的，我国有权采取相应反制措施。
            """,
            "summary": "明确反对外国干涉内政，确立反制措施的法律依据。",
            "effective_date": datetime(2021, 6, 10)
        },
        {
            "code": "PRC-AFS-6",
            "name_zh": "中华人民共和国反外国制裁法第6条 - 反制措施",
            "category": "国内法",
            "level": "法律",
            "region": "CN",
            "content": """
国务院有关部门可以按照各自职责和任务分工，对列入反制清单的个人、组织，根据实际情况决定采取下列一种或者几种措施：
（一）不予签发签证、不准入境、注销签证或者驱逐出境；
（二）查封、扣押、冻结在我国境内的动产、不动产和其他各类财产；
（三）禁止或者限制我国境内的组织、个人与其进行有关交易、合作等活动；
（四）其他必要措施。
            """,
            "summary": "列举具体的反制措施：拒签、冻结资产、禁止交易。",
            "effective_date": datetime(2021, 6, 10)
        },
        {
            "code": "PRC-AFS-12",
            "name_zh": "中华人民共和国反外国制裁法第12条 - 不受外国法院管辖",
            "category": "国内法",
            "level": "法律",
            "region": "CN",
            "content": """
任何组织和个人均不得执行或者协助执行外国国家对我国公民、组织采取的歧视性限制措施。
组织和个人违反前款规定，侵害我国公民、组织合法权益的，我国公民、组织可以依法向人民法院提起诉讼，要求其停止侵害、赔偿损失。
            """,
            "summary": "禁止在中国境内执行外国歧视性制裁。",
            "effective_date": datetime(2021, 6, 10)
        },

        # --- Vienna Convention on the Law of Treaties (VCLT) ---
        {
            "code": "VCLT-26",
            "name_zh": "维也纳条约法公约第26条 - 约定必守 (Pacta Sunt Servanda)",
            "category": "国际法",
            "level": "国际公约",
            "region": "UN",
            "content": """
凡有效之条约，对于其当事国均有拘束力，必须由各该国善意履行。
            """,
            "summary": "条约法的基础原则，要求依约履行。",
            "effective_date": datetime(1980, 1, 27)
        },
        {
            "code": "VCLT-31",
            "name_zh": "维也纳条约法公约第31条 - 解释之通则",
            "category": "国际法",
            "level": "国际公约",
            "region": "UN",
            "content": """
1. 条约应依其用语按其上下文并参照条约之目的及宗旨所具有之通常意义，善意解释之。
2. 就解释条约而言，上下文除指连同弁言及附件在内之全文外，并应包括：
(a) 全体当事国因缔结条约所订与条约有关之任何协定；
(b) 一个或数个当事国因缔结条约所订并经其他当事国接受为与条约有关之文书。
            """,
            "summary": "确立条约解释的黄金规则：通常意义、上下文、目的及宗旨。",
            "effective_date": datetime(1980, 1, 27)
        },
        {
            "code": "VCLT-62",
            "name_zh": "维也纳条约法公约第62条 - 情势之根本改变 (Rebus Sic Stantibus)",
            "category": "国际法",
            "level": "国际公约",
            "region": "UN",
            "content": """
1. 条约缔结时存在之情势发生根本改变，非当事国所预见，且此项改变之存在构成当事国同意受条约拘束之主要根据，及该项改变之影响将根本变动依条约尚待履行之义务之范围者，不得援引该项根本改变作为终止或退出条约之理由，除非：
(a) 该项改变之存在构成当事国同意受条约拘束之必要根据；及
(b) 该项改变之影响将根本变动依条约尚待履行之义务之性质。
2. 边界条约不得援引情势根本改变作为终止或退出之理由。
            """,
            "summary": "情势变更原则，允许在极端情况下终止条约，但边界条约除外。",
            "effective_date": datetime(1980, 1, 27)
        },

        # --- Additional UNCLOS Articles ---
        {
            "code": "UNCLOS-87",
            "name_zh": "联合国海洋法公约第87条 - 公海自由",
            "category": "海洋法",
            "level": "国际公约",
            "region": "UN",
            "content": """
1. 公海对所有国家开放，不论其为沿海国或内陆国。公海自由是在本公约和其他国际法规则所规定的条件下行使的。公海自由对沿海国和内陆国而言，除其他外，包括：
(a) 航行自由；
(b) 飞越自由；
(c) 铺设海底电缆和管道的自由...
(d) 建造国际法所允许的人工岛屿和其他设施的自由...
(e) 捕鱼自由...
(f) 科学研究自由...
2. 这些自由应由所有国家行使，但须适当顾及其他国家行使公海自由的利益。
            """,
            "summary": "列举了公海六大自由。",
            "effective_date": datetime(1994, 11, 16)
        },
        {
            "code": "UNCLOS-76",
            "name_zh": "联合国海洋法公约第76条 - 大陆架的定义",
            "category": "海洋法",
            "level": "国际公约",
            "region": "UN",
            "content": """
1. 沿海国的大陆架包括其领海以外依其陆地领土的全部自然延伸，扩展到大陆边外缘的海底区域的海床和底土，如果从测算领海宽度的基线量起至大陆边外缘的距离不到二百海里，则扩展到二百海里的距离。
            """,
            "summary": "定义大陆架范围，最大可达350海里或2500米等深线外100海里。",
            "effective_date": datetime(1994, 11, 16)
        },

        # --- UN Charter ---
        {
            "code": "UN-CHARTER-2-4",
            "name_zh": "联合国宪章第2条第4项 - 禁止使用武力",
            "category": "联合国宪章",
            "level": "国际公约",
            "region": "UN",
            "content": """
各会员国在其国际关系上不得使用威胁或武力，或以与联合国宗旨不符之任何其他方法，侵害任何会员国之领土完整或政治独立。
            """,
            "summary": "现代国际法基石，禁止在国际关系中使用武力。",
            "effective_date": datetime(1945, 10, 24)
        },
        # --- UN Charter ---

        {
            "code": "UN-CHARTER-51",
            "name_zh": "联合国宪章第51条 - 自卫权",
            "category": "联合国宪章",
            "level": "国际公约",
            "region": "UN",
            "content": """
联合国任何会员国受武力攻击时，在安全理事会采取必要办法，以维持国际和平及安全以前，本宪章不得认为禁止行使单独或集体自卫之自然权利。会员国因行使此项自卫权而采取之办法，应立向安全理事会报告，此项办法于任何方面不得影响该会按照本宪章随时采取其所认为必要行动之权责，以维持或恢复国际和平及安全。
            """,
            "summary": "规定了国家在遭受武装攻击时的固有自卫权。",
            "effective_date": datetime(1945, 10, 24)
        }
    ]

    # --- Programmatic Generation for Scaled Data (Goal: >100) ---
    extra_categories = {
        "核武法": ["NPT", "TPNW", "IAEA-Safe"],
        "战争法": ["Geneva-I", "Geneva-II", "Geneva-III", "Geneva-IV", "Hague"],
        "环境法": ["Paris-Agree", "CBD", "UNFCCC", "Plastic-Treaty"],
        "领土法": ["Antarctic", "Space-Treaty", "Moon-Agree"],
        "网络法": ["Tallinn-Manual", "Budapest-Conv"]
    }

    # Generate placeholders to reach target count if needed, but let's try to make them semi-realistic
    base_laws = [
        # Nuclear
        ("NPT-Art1", "不扩散核武器条约第1条", "核武法", "核武器国家承诺不转让核武器。"),
        ("NPT-Art2", "不扩散核武器条约第2条", "核武法", "无核武器国家承诺不接收核武器。"),
        ("NPT-Art4", "不扩散核武器条约第4条", "核武法", "和平利用核能的权利。"),
        ("NPT-Art6", "不扩散核武器条约第6条", "核武法", "就停止核军备竞赛和核裁军进行谈判。"),
        ("TPNW-Art1", "禁止核武器条约第1条", "核武法", "全面禁止开发、试验、生产、制造、获取、拥有或储存核武器。"),

        # War (Geneva)
        ("GC-I-Art12", "日内瓦第一公约第12条", "战争法", "伤者和病者应受尊重和保护。"),
        ("GC-III-Art13", "日内瓦第三公约第13条", "战争法", "战俘必须始终受到人道待遇。"),
        ("GC-IV-Art32", "日内瓦第四公约第32条", "战争法", "禁止对受保护人员施加体罚或酷刑。"),
        ("AP-I-Art48", "第一附加议定书第48条", "战争法", "区分原则：区分平民居民和战斗员。"),
        ("AP-I-Art51", "第一附加议定书第51条", "战争法", "平民居民应享有的保护，免受军事行动危险。"),

        # Environment
        ("Paris-Art2", "巴黎协定第2条", "环境法", "将全球平均气温升幅控制在2℃以内。"),
        ("CBD-Art3", "生物多样性公约第3条", "环境法", "各国拥有开发其资源的主权权利，并负有不损害他国环境的责任。"),
        ("UNFCCC-Art3", "气候变化框架公约第3条", "环境法", "共同但有区别的责任原则。"),

        # Territory / Space
        ("OST-Art2", "外空条约第2条", "领土法", "外空不得由任何国家通过主权要求据为己有。"),
        ("OST-Art4", "外空条约第4条", "领土法", "禁止在绕地球轨道放置核武器或其他大规模毁灭性武器。"),
        ("Antarctic-Art1", "南极条约第1条", "领土法", "南极应仅用于和平目的。"),

        # Cyber
        ("Tallinn-Rule1", "塔林手册规则1", "网络法", "国家对网络基础设施的主权。"),
        ("Tallinn-Rule10", "塔林手册规则10", "网络法", "禁止网络干涉内政。"),
    ]

    for i, (code, name, cat, sum_text) in enumerate(base_laws):
        laws_data.append({
            "code": code,
            "name_zh": name,
            "category": cat,
            "level": "国际公约",
            "region": "Intl",
            "content": f"{name} 的具体内容...\n(此处为模拟的法律文本，用于系统演示)\n{sum_text}",
            "summary": sum_text,
            "effective_date": datetime(2000, 1, 1)
        })

    # Generate generic laws to fill up to 100
    current_count = len(laws_data)
    target_count = 105

    domains = ["海洋法", "国际法", "战争法", "环境法", "商法", "刑法", "行政法"]

    for i in range(target_count - current_count):
        domain = domains[i % len(domains)]
        idx = i + 1
        laws_data.append({
            "code": f"GEN-LAW-{domain[:2].upper()}-{idx:03d}",
            "name_zh": f"模拟{domain}条款 #{idx}",
            "category": domain,
            "level": "模拟法规",
            "region": "Global",
            "content": f"这是关于 {domain} 的第 {idx} 条模拟条款。\n旨在测试系统在大规模数据下的表现。",
            "summary": f"关于 {domain} 的模拟规定 {idx}。",
            "effective_date": datetime(2023, 1, 1)
        })

    count = 0
    for data in laws_data:
        # Check if exists
        existing = db.query(Law).filter(Law.code == data["code"]).first()
        if not existing:
            law = Law(**data)
            db.add(law)
            print(f"Added law: {data['code']}")
            count += 1
        else:
            print(f"Law {data['code']} already exists, skipping.")

    db.commit()
    print(f"\\nSeeding complete. Added {count} new laws.")
    db.close()

if __name__ == "__main__":
    seed_laws()
