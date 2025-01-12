from random import randint

pgr_builtin_tips = [
    "!!",
    "(Not) Sound Only",
    "(•▴• )咕咕～",
    "72788433374733678633778263464",
    ":( :手法.exe未响应，如果继续推进会导致推分失败。是否继续？ 【休息一下/强行推进】",
    "[此条Tip已被隐藏]",
    "AT的意思并不是Anti-Thumb（",
    "Compute It With Some...什么来着?",
    "CONDITIO SINE QUA NON",
    "E! S! M! Power!",
    "EZ是摁着而非Easy，HD是高清而非Hard，IN是里面而非Insane，AT是位于而非Another，等会我是不是说反了？",
    "Full Combo就是打中所有note咕！",
    "Hit me with the HARDCORE!!!",
    "INTeRneT ENERGY -Overdose-",
    "Let's! Get! Higher!!!",
    "NO ONE YES PIGEONS",
    "One! Two! Three! Fire!!!",
    "phigrOS正在加载中...",
    "print(\"Hello tips3.0\");",
    "Redemption.",
    "rks是RankingScore，不是热开水！（认真脸）",
    "Saturn新闻频道：插播一条紧急播报，请不要看向晚上的天空或月亮。",
    "See You Next Time",
    "sudo 板子自己打歌",
    "Tell Me Your Secret",
    "This is the story for one character of misery",
    "Tip: Tip: Tip: Tip: Tip: Tip: Tip: Tip: Tip:",
    "top10我最喜欢的鸽子——top1：鸠！",
    "WHAT DO YOU KNOW WHAT DO YOU PLAY WHAT DO YOU REMEMBER WHAT DO YOU LOVE",
    "WOW 虫眼！",
    "Yooooooooooooooooooo",
    "按键大小不舒服？在设置中可以调整大小！",
    "阿鸠你又在反复看Tips了哦",
    "啊！PhigrOS又崩溃了......",
    "啊！要给你看什么Tip好呢...(翻",
    "啊～啊～啊咦↑啊咦↑啊→啊↑啊↓啊～啊～",
    "别慌！这只是个鸽子陷阱而已啦~",
    "不是，鸽们",
    "不要的显卡统统可以拿到Pigeon Animation Team换不锈钢脸盆",
    "不要喝奇怪的品红色药水！",
    "不要烤翅……",
    "不要在意他人对你说什么，你独一无二，你是你自己的光",
    "彩~虹~课~题~模~式~",
    "猜猜看你要重新加载多少次才能再看到这条tip ￣︶￣",
    "当你在看这行字的时候 我就知道 你肯定在看这行字",
    "当你在三次觉得诸事不顺的时候，看看现在的打歌成绩，比起刚入坑的时候，是不是提高了很多？现在也是哦，你一直都在成长",
    "打击头部不会使更新速度加快",
    "噔噔噔 噔噔 噔噔 噔噔噔噔噔噔",
    "对不起，您所拨打的电话号码是空号-Sorry, the number you dialed does not exist",
    "多多游玩Phigros有助于放松手指以及锻炼大脑协调能力哦！",
    "诶……防脱洗发水用完了……",
    "饿啊！咕咕咕咕",
    "扉格晚五点，周五准时更新！",
    "分数我所欲也，acc亦我所欲也，若二者不可得兼，多练也。",
    "附近 5 米内，有一只鸽子，正在靠近......",
    "感谢各位小鸽子们陪伴我们走过了五个年头",
    "高三党，现在，立刻，去给我学习！！！",
    "给多押note镀层金，我就是这个谱面里最靓的仔",
    "歌曲可以用标题、难度、分数的分类顺序或逆序排序咕！",
    "鸽游的烧烤摊包含了驴肉、欧芹、油条、完全熟不透的牛角等等，唯独就是没有烤翅……",
    "歌终有一收，而有些需要一点小小的帮助（指旋转设备",
    "咕咕咕~如果你正开心，希望Phigros能让你笑颜常开哦！",
    "咕咕咕~如果你正糟心，希望Phigros能带你扬眉吐气哦！",
    "咕咕咕！请不要在任何无关场合提及Phigros哦！谢谢配合！咕咕咕！",
    "欢迎回到Phigros！",
    "欢迎在B站@Phigros官方 关注我们！",
    "活用垂直判定可以打出很多炫酷的手法！",
    "江源速报：多地出现无故昏厥人员，卫生部呼吁民众注意饮食健康",
    "江源速报：警方发表惊人结果，何琼语原系自杀身亡",
    "江源速报：巨塔效应急剧化，神秘群体林泊浮出水面",
    "江源速报：名人自杀现象异常扩散，知名作家留下诡异遗书",
    "江源速报：拟态系统PhigrOS，将于8月31号正式上线",
    "江源速报：全球年均温再度上升，重返地表签名破千万",
    "江源速报：群体性臆症爆发，多人自称蜂巢C区存在巨塔",
    "江源速报：三大基地全面开放通行，冰封纪元即将结束？",
    "江源速报：上半年人口增长率再创新低，新型受精技术受挫",
    "江源速报：政府出台就业新策，望促进失业人员再就业",
    "江源速报：知名歌手何琼语于昨夜凌晨意外死亡，凶手仍在追查中",
    "江源速报：专家呼吁复兴AI产业，以应对劳动力紧缺问题",
    "假如，我是说假如，判定线能够自由地动起来...",
    "今日打歌对决强者谱面，恐怖配置猛如鬼神，拼尽全力战胜它！",
    "进入设置后可以更换头像与名片背景",
    "今天的随机歌曲是......？",
    "鸠和基诺会一直陪伴着你。只要你不卸载Phigros的话！",
    "鸠：“我可以成为偶像吗？”",
    "觉得太简单的话，可以试试课题模式哦！",
    "聚是一团鸽，散作满天鸽",
    "开启多押提示可以更好地帮助你找准歌曲节奏",
    "看到了比较怪异而难以下手的配置？谱面之中往往存在提示，睁大眼睛仔细观察吧。",
    "看，那里有一个“note”",
    "课题模式会更难拿到All Perfect……好难……",
    "快睡觉吧，熬夜对身体不好",
    "来猜猜看这边有几个有用的信息呢~",
    "来唱歌！ 咕！咕！咕咕咕！",
    "落到判定线上的note竟然不是这根判定线的……！",
    "冷知识：这是一条……阿嚏！……冷知识！",
    "面对满屏幕的按键感到不知所措？可以多多尝试以发现其中的规律。",
    "你AP了，就一定AP了吧！",
    "你打一首歌的时间，鸠已经发现 NaN 个问题了",
    "你看这个巨型鸽子，它已经吃了-1个note了……？",
    "你看这个巨型鸽子，它已经吃了2147483647个note了……嗯怎么突然消失了！",
    "你们熟知的PV组已经正式更名为Pigeon Animation Team了哦（怎么这么长）",
    "你先别急！！这不有云存档嘛",
    "你喜欢上面这张曲绘么？",
    "你知道吗？鸽游于2019年2月8号成立， 8月31号则是Phigros的生日哦",
    "你知道吗？其实tips全都是废话（确信",
    "谱面难点各有千秋，因人而异，因地力制宜（？",
    "前排出售美味鸽粮咕～",
    "请给我们的pv组捐点硬盘吧！！非常感谢！",
    "热知识：这是一条……烫烫烫烫烫！的热知识。",
    "如果不想被打断，那就开启手机的免打扰吧！",
    "如果打歌感到不舒畅，起身走走，然后回来，会好很多。",
    "如果觉得推分乏力，容易反复失误的话，可以试试谱面镜像功能哦~",
    "如果没法决定玩哪首歌，何不试试随机曲目功能呢～",
    "如果你想打得更精准一些，可以尝试使用节拍器（？）",
    "如果想要挑战自己，可以试一试课题模式？",
    "如何玩好Phigros：第一步：玩Phigros！",
    "如何游玩粉键？↑←↙→↗↓↖↗↓↑→↙←……",
    "如何做到毫无创作瓶颈？答案是有瓶颈的时候不创作",
    "赛博鸽子会梦到Phigros吗（",
    "上次看到这条Tip还是上次",
    "声音传播需要介质",
    "设备性能不足的小鸽子们可以使用设置中的低分辨率模式来获得更流畅的体验。",
    "时针滴滴答答在走，这首歌你φ了没有？",
    "手持两把锟斤拷，口中疾呼烫烫烫",
    "帅鸽的话，只要像这样，dong~dong~dong~，就可以快速收歌哦。来，试试看！",
    "数数这里一共有多少条tips？",
    "堂  堂  联  动",
    "听说完成主线后，小鸽子们的Phigros都发生了不小的外观变化……",
    "听说有时候次难度也会整大活，赶紧来试试吧！",
    "提问！你还记得上一条tip是什么吗？",
    "突然来了一条消息！                   哦这里是tips啊，那没事了",
    "完成主线之后，课题模式就会解锁哦！",
    "玩久了，一定要记得闭上眼睛休息一会儿哦~",
    "为防误触，暂停键需要点两次才可以暂停。",
    "为什么有些难度没有解锁啊！——因为你的前一难度的成绩还没达到S哦，请多多努力吧！",
    "我被困在林泊百科里了！救命！",
    "我变成鸽子了！！！",
    "我超，劲爆",
    "我的转板不会输！",
    "我觉得生发剂不一定有用，得植发",
    "我们的口号是？咕咕咕！",
    "我们通过大数据分析您的喜好查找能获得更高浏览量的tips。",
    "我们在EZ、HD谱面上也下了很多功夫咕~",
    "我确信我发现了一个能百分百拿到φ的绝妙手法，可惜Tip的长度太短了，写不下。",
    "我相信你。",
    "物量不代表难度喔咕咕！",
    "像素塔真的存在吗。",
    "想要5000TB Data！",
    "想要提升rks的话，尝试把困难的谱面打得更准咕！",
    "现在！快看向外面的月亮！",
    "小鸽子们不要挑食哦，不管是烤鸭还是欧芹都要吃~",
    "小鸽子们也要多多支持其他音乐游戏哟~",
    "小心翼翼千万别被发现",
    "下次的成绩一定会更好！",
    "下次一定会更好！",
    "兄弟！你好强！",
    "兄弟，鸽子不错，摸摸",
    "希望Phigros能陪伴你们到天长地久，抱抱",
    "音游关卡就像海洋，只有意志坚强的人，才能到达φ的彼岸",
    "有没有数过这是你第几次看到这条tips呢？",
    "有时候Note本身也可以充当判定线的替身哦",
    "有些音符会跟随音高排列哦，用心感受音乐的律动吧～",
    "有一个人前来打歌",
    "愿大家都能板子不吃音打出好成绩",
    "愿小鸽子们都能在课题中达到“此地有金三百万”",
    "与普遍的看法相反，opia不是一首关于眼病的歌",
    "在B站@Phigros官方 关注我们以获取最新的更新预告咕！",
    "在遇到游戏音频出现异常的时候，试试拉高下设置>其他>音频问题疑难解答中的值哦！",
    "这个才是真的note哦~（miss）",
    "这里是鸽游！",
    "这里为什么会有note啦！",
    "这日子是越来越有判头了（指判定线",
    "这是一条来自1.0.0版本的Tip！（错乱）",
    "这是一条属于3.0版本的Tip！",
    "这张谱看起来好可怕......",
    "众所周知，鸽游一年有377天",
    "主线章节一~四已整理进Legacy章节。",
    "自从使用了同步存档，手也不酸了，头也不痛了，推分也来劲了！",
    "总觉得对不上节奏？试试在设置中调整偏移吧！",
    "φ？拿来吧你！",
    "← To Be Continued...",
    "♪Play like you never did before~",
    "♪Wish upon a satellite...",
    "♪别忘记今天好好享受毋庸置疑，明天是明天仍留有期待心情~",
    "《5年课题，3年单曲》"
]

ppr_extended_tips = [
    "https://github.com/qaqFei/PhigrosPlayer",
    "你知道吗, float('nan') != float('nan') 哦",
    "本项目是使用MIT协议开源的哦!",
    "(╯‵□′)╯",
    "你说的对，但是《lchzh3473模拟器》是由李纯真自主研发的一款全新开放世界冒险游戏。游戏发生在一个被称作「Phigros」的幻想世界，在这里，被李纯真选中的人将被授予「举办」，导引视频删除之力。你将扮演一位名为「沉默-_-微笑」的神秘角色，在自由的旅行中邂逅性格各异、能力独特的补档们，和他们一起击败李纯真，找回失散的视频——同时，逐步发掘「lchzh3473模拟器」的真相。",
    "诶, 怎么卡住了, 咚！Traceback (most recent call last)",
    "嗯... 这是什么, 哦！Exception！让我们 logging.fatal",
    "哎呀！(转头) >>> del error_*.txt"
]

tips = [
    *pgr_builtin_tips,
    *ppr_extended_tips
]

def get_tip():
    return tips[randint(0, len(tips) - 1)]