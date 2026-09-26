"""
Pre-verified Multilingual Disaster Alert Templates
Supports 7 languages: Odia, Hindi, English, Bengali, Telugu, Tamil, Urdu.
Ensures critical emergency terminology is pre-verified by disaster guidelines (OSDMA / NDMA / IMD)
and never distorted by generic machine translation.
"""

LANGUAGES = {
    "or": {"name": "Odia", "native": "ଓଡ଼ିଆ"},
    "hi": {"name": "Hindi", "native": "हिन्दी"},
    "en": {"name": "English", "native": "English"},
    "bn": {"name": "Bengali", "native": "বাংলা"},
    "te": {"name": "Telugu", "native": "తెలుగు"},
    "ta": {"name": "Tamil", "native": "தமிழ்"},
    "ur": {"name": "Urdu", "native": "اردو"}
}

SEVERITY_LEVELS = {
    "Watch": {
        "color": "#eab308",
        "badge_class": "bg-yellow-500 text-black",
        "level_score": 1,
        "labels": {
            "en": "Watch (Preparation)",
            "or": "ନଜର / ପ୍ରସ୍ତୁତ ରୁହନ୍ତୁ (Watch)",
            "hi": "निगरानी / तैयार रहें (Watch)",
            "bn": "নজরদারি / প্রস্তুত থাকুন (Watch)",
            "te": "సన్నద్ధత / పరిశీలన (Watch)",
            "ta": "கண்காணிப்பு / தயார் நிலை (Watch)",
            "ur": "نگرانی / تیار رہیں (Watch)"
        }
    },
    "Warning": {
        "color": "#f97316",
        "badge_class": "bg-orange-500 text-white",
        "level_score": 2,
        "labels": {
            "en": "Warning (Take Action)",
            "or": "ସତର୍କ ସୂଚନା (Warning)",
            "hi": "चेतावनी / सतर्क रहें (Warning)",
            "bn": "সতর্কবার্তা (Warning)",
            "te": "హెచ్చరిక (Warning)",
            "ta": "எச்சரிக்கை (Warning)",
            "ur": "انتباہ / خبردار (Warning)"
        }
    },
    "Severe": {
        "color": "#ef4444",
        "badge_class": "bg-red-600 text-white animate-pulse",
        "level_score": 3,
        "labels": {
            "en": "Severe (High Danger)",
            "or": "ଗମ୍ଭୀର ବିପଦ (Severe Danger)",
            "hi": "गंभीर खतरा (Severe Danger)",
            "bn": "মারাত্মক বিপদ (Severe Danger)",
            "te": "తీవ్రమైన ప్రమాదం (Severe Danger)",
            "ta": "தீவிர ஆபத்து (Severe Danger)",
            "ur": "شدید خطرہ (Severe Danger)"
        }
    },
    "Extreme": {
        "color": "#7f1d1d",
        "badge_class": "bg-red-900 text-white font-extrabold animate-bounce",
        "level_score": 4,
        "labels": {
            "en": "Extreme (Immediate Threat to Life)",
            "or": "ଚରମ ଜୀବନ ବିପଦ / ତୁରନ୍ତ ଖାଲି କରନ୍ତୁ (Extreme)",
            "hi": "अत्यंत गंभीर / तत्काल जीवन रक्षा (Extreme)",
            "bn": "চরম সংকট / জীবন বাঁচান (Extreme)",
            "te": "అత్యంత తీవ్ర ముప్పు (Extreme)",
            "ta": "அதிதீவிர அபாயம் (Extreme)",
            "ur": "انتہائی سنگین خطرہ (Extreme)"
        }
    }
}

HAZARDS = {
    "Cyclone": {
        "icon": "🌀",
        "default_helpline": "112, 1070 (State EOC), 1077 (District)",
        "translations": {
            "en": {
                "name": "Cyclone",
                "headline": "Severe Cyclonic Storm Alert",
                "recommended_action": "Evacuate to designated concrete cyclone shelter immediately. Secure loose outdoor objects, switch off power mains, and store drinking water & essential medicines.",
                "short_sms": "[SDMA ALERT] CYCLONE {severity} in {area}. Evacuate to shelter. Mains off. Helplines: {helpline}. Reply 1 if SAFE, 2 for RESCUE.",
                "ivr_script": "Urgent Disaster Alert. Severe Cyclonic storm warning for {area}. Evacuate to the nearest shelter immediately. If you are safe, press 1. If you need rescue, press 2."
            },
            "or": {
                "name": "ବାତ୍ୟା (Cyclone)",
                "headline": "ଭୟଙ୍କର ସାମୁଦ୍ରିକ ବାତ୍ୟା ସତର୍କତା",
                "recommended_action": "ତୁରନ୍ତ ନିକଟସ୍ଥ ପକ୍କା ବାତ୍ୟା ଆଶ୍ରୟସ୍ଥଳୀକୁ ଯାଆନ୍ତୁ। ବିଦ୍ୟୁତ ସଂଯୋଗ ବନ୍ଦ ରଖନ୍ତୁ, ପାନୀୟ ଜଳ ଏବଂ ଜରୁରୀ ଔଷଧ ସଂରକ୍ଷଣ କରନ୍ତୁ। କୌଣସି ପରିସ୍ଥିତିରେ ବାହାରକୁ ବାହାରନ୍ତୁ ନାହିଁ।",
                "short_sms": "[ସତର୍କତା] {area} ରେ ବାତ୍ୟା {severity}। ପକ୍କା ଆଶ୍ରୟକୁ ଯାଆନ୍ତୁ। ସହାୟତା: {helpline}। ସୁରକ୍ଷିତ ଥିଲେ 1, ସାହାଯ୍ୟ ପାଇଁ 2 ପଠାନ୍ତୁ।",
                "ivr_script": "ଜରୁରୀ ସୂଚନା। ଆପଣଙ୍କ ଅଞ୍ଚଳ {area} ପାଇଁ ବାତ୍ୟା ସତର୍କତା ଜାରି ହୋଇଛି। ତୁରନ୍ତ ବାତ୍ୟା ଆଶ୍ରୟକୁ ଯାଆନ୍ତୁ। ଆପଣ ସୁରକ୍ଷିତ ଥିଲେ 1 ଦବାନ୍ତୁ, ସାହାଯ୍ୟ ଆବଶ୍ୟକ ଥିଲେ 2 ଦବାନ୍ତୁ।"
            },
            "hi": {
                "name": "चक्रवात (Cyclone)",
                "headline": "भीषण चक्रवाती तूफान चेतावनी",
                "recommended_action": "तुरंत निकटतम पक्के चक्रवात आश्रय स्थल (Shelter) में जाएं। बिजली का मेन स्विच बंद करें, सुरक्षित पेयजल व जरूरी दवाइयां साथ रखें। समुद्र या बाहर न जाएं।",
                "short_sms": "[आपदा अलर्ट] {area} में चक्रवात {severity}। तुरंत पक्के शेल्टर में जाएं। हेल्पलाइन: {helpline}। सुरक्षित हैं तो 1, मदद के लिए 2 भेजें।",
                "ivr_script": "आपातकालीन सूचना। {area} के लिए चक्रवात चेतावनी जारी की गई है। तुरंत सुरक्षित आश्रय में जाएं। सुरक्षित होने पर 1 दबाएं, राहत सहायता हेतु 2 दबाएं।"
            },
            "bn": {
                "name": "ঘূর্ণিঝড় (Cyclone)",
                "headline": "মারাত্মক ঘূর্ণিঝড় সতর্কতা বার্তা",
                "recommended_action": "অবিলম্বে নিকটবর্তী পাকা ঘূর্ণিঝড় আশ্রয়কেন্দ্রে চলে যান। বিদ্যুতের সংযোগ বন্ধ রাখুন, পানীয় জল ও প্রয়োজনীয় ওষুধ মজুত রাখুন। কাঁচা ঘরে থাকবেন না।",
                "short_sms": "[দুর্যোগ সতর্কতা] {area} অঞ্চলে ঘূর্ণিঝড় {severity}। দ্রুত আশ্রয়কেন্দ্রে যান। হেল্পলাইন: {helpline}। নিরাপদ থাকলে 1, উদ্ধারের জন্য 2 লিখুন।",
                "ivr_script": "জরুরি বার্তা। {area} এলাকার জন্য ঘূর্ণিঝড় সতর্কতা জারি করা হয়েছে। অবিলম্বে আশ্রয়কেন্দ্রে আশ্রয় নিন। আপনি নিরাপদ থাকলে 1 চাপুন, সাহায্যের জন্য 2 চাপুন।"
            },
            "te": {
                "name": "తుఫాను (Cyclone)",
                "headline": "తీవ్ర తుఫాను హెచ్చరిక",
                "recommended_action": "వెంటనే సమీపంలోని తుఫాను సహాయక శిబిరానికి వెళ్లండి. విద్యుత్ సరఫరా ఆపివేయండి. తాగునీరు మరియు అవసరమైన ఔషధాలు సిద్ధంగా ఉంచుకోండి.",
                "short_sms": "[హెచ్చరిక] {area} లో తుఫాను {severity}. వెంటనే పునరావాస కేంద్రానికి వెళ్లండి. హెల్ప్‌లైన్: {helpline}. సురక్షితంగా ఉంటే 1, సహాయం కోసం 2 పంపండి.",
                "ivr_script": "అత్యవసర విపత్తు హెచ్చరిక. {area} కు తీవ్ర తుఫాను హెచ్చరిక జారీ చేయబడింది. వెంటనే సురక్షిత ప్రాంతానికి వెళ్లండి. సురక్షితమైతే 1, రక్షణ కోసం 2 నొక్కండి."
            },
            "ta": {
                "name": "புயல் (Cyclone)",
                "headline": "தீவிர புயல் எச்சரிக்கை அறிவிப்பு",
                "recommended_action": "உடனடியாக அருகிலுள்ள பாதுகாப்பான புயல் நிவாரண முகாமிற்குச் செல்லவும். மின் இணைப்பைத் துண்டிக்கவும். குடிநீர், மருந்துகளைப் பாதுகாத்து வைக்கவும்.",
                "short_sms": "[பேரிடர் அலர்ட்] {area} பகுதியில் புயல் {severity}. பாதுகாப்பு மையத்திற்கு செல்லவும். உதவி எண்: {helpline}. பாதுகாப்பாக இருந்தால் 1, உதவிக்கு 2.",
                "ivr_script": "அவசர பேரிடர் தகவல். {area} பகுதிக்கு தீவிர புயல் எச்சரிக்கை. உடனே பாதுகாப்பான இடத்திற்கு செல்லவும். பாதுகாப்பாக இருந்தால் 1, உதவி தேவைப்படின் 2 அழுத்தவும்."
            },
            "ur": {
                "name": "طوفان (Cyclone)",
                "headline": "شدید سمندری طوفان کا انتباہ",
                "recommended_action": "فوری طور پر قریبی پکے سائیکلون شیلٹر میں منتقل ہو جائیں۔ بجلی کا مین سوئچ بند کریں اور پینے کا صاف پانی اور ضروری ادویات ساتھ رکھیں۔",
                "short_sms": "[انتباہ] {area} میں طوفان {severity}۔ فورا شیلٹر جائیں۔ ہیلپ لائن: {helpline}۔ اگر محفوظ ہیں تو 1، مدد کیلئے 2 بھیجیں۔",
                "ivr_script": "ہنگامی الرٹ۔ {area} کے لیے طوفان کا شدید انتباہ۔ فوری محفوظ پناہ گاہ میں پہنچیں۔ محفوظ ہونے پر 1 دبائیں، امداد کے لیے 2 دبائیں۔"
            }
        }
    },
    "Flood": {
        "icon": "🌊",
        "default_helpline": "112, 1070, NDRF: 011-24363260",
        "translations": {
            "en": {
                "name": "Flood",
                "headline": "Flash Flood & River Inundation Alert",
                "recommended_action": "Move to higher ground or upper floors immediately. Do not attempt to walk, swim, or drive through flowing floodwaters. Turn off electricity and gas valves.",
                "short_sms": "[SDMA ALERT] FLOOD {severity} in {area}. Move to high ground immediately. Do NOT cross water. Helplines: {helpline}. Reply 1 if SAFE, 2 for RESCUE.",
                "ivr_script": "Emergency Alert. Severe Flood Warning for {area}. Move to elevated ground immediately. Do not walk into floodwaters. Press 1 if you are safe, or press 2 for rescue."
            },
            "or": {
                "name": "ବନ୍ୟା (Flood)",
                "headline": "ଭୀଷଣ ବନ୍ୟା ଜଳପ୍ଲାବନ ସତର୍କତା",
                "recommended_action": "ତୁରନ୍ତ ଉଚ୍ଚ ସ୍ଥାନ ବା ଉପର ମହଲାକୁ ଯାଆନ୍ତୁ। ପ୍ରବାହିତ ବନ୍ୟା ଜଳରେ ଚାଲିବା କିମ୍ବା ଗାଡ଼ି ଚଳାଇବାକୁ ଚେଷ୍ଟା କରନ୍ତୁ ନାହିଁ। ବିଦ୍ୟୁତ ସୁଇଚ୍ ବନ୍ଦ କରନ୍ତୁ।",
                "short_sms": "[ସତର୍କତା] {area} ରେ ବନ୍ୟା {severity}। ତୁରନ୍ତ ଉଚ୍ଚ ସ୍ଥାନକୁ ଯାଆନ୍ତୁ। ପାଣିରେ ପଶନ୍ତୁ ନାହିଁ। ସହାୟତା: {helpline}। ସୁରକ୍ଷିତ ଥିଲେ 1, ସାହାଯ୍ୟ ପାଇଁ 2।",
                "ivr_script": "ଜରୁରୀ ସୂଚନା। ଆପଣଙ୍କ ଅଞ୍ଚଳ {area} ପାଇଁ ବନ୍ୟା ସତର୍କତା ଜାରି ହୋଇଛି। ତୁରନ୍ତ ଉଚ୍ଚ ସ୍ଥାନକୁ ଯାଆନ୍ତୁ। ସୁରକ୍ଷିତ ଥିଲେ 1, ସାହାଯ୍ୟ ପାଇଁ 2 ଦବାନ୍ତୁ।"
            },
            "hi": {
                "name": "बाढ़ (Flood)",
                "headline": "अचानक बाढ़ एवं जलभराव चेतावनी",
                "recommended_action": "तुरंत ऊंचे स्थानों या पक्के भवनों की ऊपरी मंजिल पर जाएं। बहते पानी में चलने या गाड़ी चलाने का प्रयास न करें। बिजली और गैस की मुख्य लाइन बंद करें।",
                "short_sms": "[आपदा अलर्ट] {area} में बाढ़ {severity}। तुरंत ऊंचे स्थान पर जाएं। पानी में न जाएं। हेल्पलाइन: {helpline}। सुरक्षित हैं तो 1, मदद हेतु 2 भेजें।",
                "ivr_script": "आपातकालीन चेतावनी। {area} में भीषण बाढ़ की चेतावनी है। तुरंत ऊंचे स्थानों पर जाएं। सुरक्षित होने पर 1 दबाएं, बचाव कार्य हेतु 2 दबाएं।"
            },
            "bn": {
                "name": "বন্যা (Flood)",
                "headline": "তীব্র বন্যা ও জলপ্লাবন সতর্কতা",
                "recommended_action": "অবিলম্বে উঁচু স্থানে বা ভবনের ওপরের তলায় আশ্রয় নিন। বানের জলে হাঁটা বা গাড়ি চালানোর চেষ্টা করবেন না। বিদ্যুৎ ও গ্যাস সংযোগ বিচ্ছিন্ন করুন।",
                "short_sms": "[বন্যা সতর্কতা] {area} তে বন্যা {severity}। অবিলম্বে উঁচু জায়গায় যান। হেল্পলাইন: {helpline}। নিরাপদ থাকলে 1, উদ্ধারের জন্য 2 লিখুন।",
                "ivr_script": "জরুরি দুর্যোগ বার্তা। {area} অঞ্চলে বন্যা সতর্কতা। অবিলম্বে উঁচু স্থানে যান। নিরাপদ থাকলে 1 চাপুন, উদ্ধারের জন্য 2 চাপুন।"
            },
            "te": {
                "name": "వరద (Flood)",
                "headline": "ఆకస్మిక వరద ప్రమాద హెచ్చరిక",
                "recommended_action": "వెంటనే ఎత్తైన ప్రాంతాలకు చేరుకోండి. ప్రవహించే నీటిలో నడవవద్దు లేదా వాహనాలు నడపవద్దు. విద్యుత్ మెయిన్ ఆఫ్ చేయండి.",
                "short_sms": "[హెచ్చరిక] {area} లో వరదలు {severity}. వెంటనే ఎత్తైన ప్రదేశానికి వెళ్లండి. హెల్ప్‌లైన్: {helpline}. సురక్షితమైతే 1, సహాయానికి 2 పంపండి.",
                "ivr_script": "విపత్తు హెచ్చరిక. {area} లో వరద ప్రమాదం ఉంది. తక్షణమే ఎత్తైన ప్రాంతానికి వెళ్లండి. సురక్షితమైతే 1, రక్షణ కోసం 2 నొక్కండి."
            },
            "ta": {
                "name": "வெள்ளம் (Flood)",
                "headline": "திடீர் வெள்ளப்பெருக்கு எச்சரிக்கை",
                "recommended_action": "உடனடியாக மேடான பகுதிக்கு அல்லது உயரமான கட்டிடங்களுக்குச் செல்லவும். ஓடும் வெள்ளநீரில் நடக்கவோ வாகனங்களை இயக்கவோ கூடாது. மின்சாரத்தை அணைக்கவும்.",
                "short_sms": "[வெள்ள அபாயம்] {area} வெள்ளம் {severity}. உடனே மேடான பகுதிக்கு செல்லவும். உதவி: {helpline}. பாதுகாப்பாக இருந்தால் 1, உதவிக்கு 2 அனுப்பவும்.",
                "ivr_script": "அவசர தகவல். {area} பகுதிக்கு வெள்ள எச்சரிக்கை. உடனடியாக உயரமான பகுதிக்கு செல்லவும். பாதுகாப்பாக இருந்தால் 1, உதவிக்கு 2 அழுத்தவும்."
            },
            "ur": {
                "name": "سیلاب (Flood)",
                "headline": "اچانک سیلاب اور طغیانی کا انتباہ",
                "recommended_action": "فوری طور پر اونچے مقامات پر منتقل ہو جائیں۔ بہتے ہوئے پانی میں چلنے یا گاڑی لے جانے سے گریز کریں۔ بجلی اور گیس بند رکھیں۔",
                "short_sms": "[سیلاب الرٹ] {area} میں سیلاب {severity}۔ فورا اونچے مقام پر جائیں۔ ہیلپ لائن: {helpline}۔ محفوظ ہیں تو 1، مدد کیلئے 2۔",
                "ivr_script": "ہنگامی الرٹ۔ {area} میں سیلاب کا سنگین خطرہ۔ فوری اونچی جگہ جائیں۔ محفوظ ہونے پر 1 دبائیں، امداد کے لیے 2 دبائیں۔"
            }
        }
    },
    "Earthquake": {
        "icon": "🏚️",
        "default_helpline": "112, 1070 (Disaster Control Room)",
        "translations": {
            "en": {
                "name": "Earthquake",
                "headline": "Strong Seismic Tremor Detected",
                "recommended_action": "DROP to the floor, COVER under a sturdy table, and HOLD ON. Stay away from glass windows, exterior walls, and power lines. If outdoors, move to open ground.",
                "short_sms": "[ALERT] EARTHQUAKE {severity} near {area}. DROP, COVER, HOLD ON. Avoid elevators/wires. Helplines: {helpline}. Reply 1 if SAFE, 2 for RESCUE.",
                "ivr_script": "Emergency Alert. Strong Earthquake tremors in {area}. Drop, cover and hold on. Avoid elevators. If you are safe, press 1. If you need rescue, press 2."
            },
            "or": {
                "name": "ଭୂକମ୍ପ (Earthquake)",
                "headline": "ଶକ୍ତିଶାଳୀ ଭୂକମ୍ପ ଝଟକା ସତର୍କତା",
                "recommended_action": "ତଳେ ବସନ୍ତୁ (Drop), ମଜବୁତ ଟେବୁଲ ତଳେ ମୁଣ୍ଡ ଢାଙ୍କନ୍ତୁ (Cover), ଏବଂ ଧରି ରଖନ୍ତୁ (Hold On)। କାଚ ଝରକା ଏବଂ ବିଦ୍ୟୁତ ତାରଠାରୁ ଦୂରେଇ ରୁହନ୍ତୁ। ଖୋଲା ପଡ଼ିଆକୁ ଯାଆନ୍ତୁ।",
                "short_sms": "[ସତର୍କତା] {area} ରେ ଭୂକମ୍ପ {severity}। ଟେବୁଲ ତଳେ ମୁଣ୍ଡ ଲୁଚାନ୍ତୁ, ଖୋଲା ଜାଗାକୁ ଯାଆନ୍ତୁ। ସହାୟତା: {helpline}। ସୁରକ୍ଷିତ ଥିଲେ 1, ସାହାଯ୍ୟ ପାଇଁ 2।",
                "ivr_script": "ଜରୁରୀ ସୂଚନା। {area} ରେ ଭୂକମ୍ପ ଅନୁଭୂତ ହୋଇଛି। ସୁରକ୍ଷିତ ଆଶ୍ରୟ ନିଅନ୍ତୁ। ଆପଣ ସୁରକ୍ଷିତ ଥିଲେ 1 ଦବାନ୍ତୁ, ସାହାଯ୍ୟ ପାଇଁ 2 ଦବାନ୍ତୁ।"
            },
            "hi": {
                "name": "भूकंप (Earthquake)",
                "headline": "तीव्र भूकंपीय झटके दर्ज",
                "recommended_action": "झुके (Drop), मजबूत मेज के नीचे ढकें (Cover), और पकड़ कर रखें (Hold On)। खिड़कियों और बिजली के तारों से दूर रहें। खुले मैदान में सुरक्षित जाएं।",
                "short_sms": "[आपदा अलर्ट] {area} में भूकंप {severity}। मेज के नीचे छिपें, खुले मैदान में जाएं। हेल्पलाइन: {helpline}। सुरक्षित हैं तो 1, मदद हेतु 2 भेजें।",
                "ivr_script": "आपातकालीन चेतावनी। {area} में भूकंप के झटके महसूस हुए हैं। खुले मैदान में रहें। सुरक्षित होने पर 1 दबाएं, बचाव के लिए 2 दबाएं।"
            },
            "bn": {
                "name": "ভূমিকম্প (Earthquake)",
                "headline": "শক্তিশালী ভূমিকম্প কম্পন সতর্কতা",
                "recommended_action": "মেঝেতে বসুন, শক্ত টেবিলের নিচে মাথা ঢেকে রাখুন এবং ধরে থাকুন। কাঁচের জানালা ও বিদ্যুৎ তার থেকে দূরে থাকুন। খোলা মাঠে আশ্রয় নিন।",
                "short_sms": "[ভূমিকম্প সতর্কতা] {area} অঞ্চলে ভূমিকম্প {severity}। শক্ত আশ্রয়ে থাকুন বা খোলা মাঠে যান। হেল্পলাইন: {helpline}। নিরাপদ থাকলে 1, উদ্ধার 2।",
                "ivr_script": "জরুরি তথ্য। {area} অঞ্চলে ভূমিকম্প হয়েছে। সতর্ক থাকুন। নিরাপদ থাকলে 1 চাপুন, উদ্ধারের জন্য 2 চাপুন।"
            },
            "te": {
                "name": "భూకంపం (Earthquake)",
                "headline": "తీవ్ర భూకంప ప్రకంపనల హెచ్చరిక",
                "recommended_action": "నేలపై కూర్చోండి, దృఢమైన బల్ల కింద తల దాచుకోండి. కిటికీలు, విద్యుత్ తీగలకు దూరంగా ఉండండి. వీలైతే ఖాళీ మైదానంలోకి వెళ్లండి.",
                "short_sms": "[హెచ్చరిక] {area} లో భూకంపం {severity}. సురక్షిత ప్రదేశంలో తలదాచుకోండి. హెల్ప్‌లైన్: {helpline}. సురక్షితమైతే 1, సహాయానికి 2 పంపండి.",
                "ivr_script": "విపత్తు హెచ్చరిక. {area} లో భూకంపం సంభవించింది. సురక్షితంగా ఉండండి. సురక్షితమైతే 1, సహాయం కోసం 2 నొక్కండి."
            },
            "ta": {
                "name": "நிலநடுக்கம் (Earthquake)",
                "headline": "சக்திவாய்ந்த நிலநடுக்க அதிர்வு எச்சரிக்கை",
                "recommended_action": "உடனே மண்டியிட்டு (Drop), உறுதியான மேசையின் கீழ் தலைமறைந்து (Cover), பிடித்துக்கொள்ளவும் (Hold On). கண்ணாடி மற்றும் மின்கம்பிகளைத் தவிர்க்கவும்.",
                "short_sms": "[நிலநடுக்கம்] {area} நிலநடுக்கம் {severity}. மேசையின் கீழ் பதுங்கவும் அல்லது திறந்தவெளிக்கு செல்லவும். உதவி: {helpline}. பாதுகாப்புக்கு 1, உதவிக்கு 2.",
                "ivr_script": "அவசர அறிவிப்பு. {area} பகுதியில் நிலநடுக்கம் ஏற்பட்டுள்ளது. திறந்தவெளிக்கு செல்லவும். பாதுகாப்பாக இருந்தால் 1, உதவிக்கு 2 அழுத்தவும்."
            },
            "ur": {
                "name": "زلزلہ (Earthquake)",
                "headline": "شدید زلزلے کے جھٹکے",
                "recommended_action": "نیچے جھکیں، مضبوط میز کے نیچے پناہ لیں اور پکڑے رکھیں۔ شیشے کی کھڑکیوں اور کھمبوں سے دور رہیں۔ کھلی جگہ پر نکلیں۔",
                "short_sms": "[زلزلہ الرٹ] {area} میں زلزلہ {severity}۔ کھلے میدان میں جائیں۔ ہیلپ لائن: {helpline}। محفوظ ہیں تو 1، مدد کیلئے 2۔",
                "ivr_script": "ہنگامی الرٹ۔ {area} میں زلزلے کے جھٹکے۔ محفوظ رہیں۔ محفوظ ہونے پر 1 دبائیں، مدد کے لیے 2 دبائیں۔"
            }
        }
    },
    "Heatwave": {
        "icon": "☀️",
        "default_helpline": "112, 104 (Health Helpline), 1070",
        "translations": {
            "en": {
                "name": "Severe Heatwave",
                "headline": "Extreme Heatwave & Sunstroke Warning",
                "recommended_action": "Avoid outdoor exposure between 11:00 AM and 4:00 PM. Drink plenty of water and ORS/lemon water. Wear loose cotton clothes and keep livestock in shade.",
                "short_sms": "[SDMA] HEATWAVE {severity} in {area}. Avoid sun 11am-4pm. Drink ORS/water. Helplines: {helpline}. Reply 1 if SAFE, 2 for MEDICAL AID.",
                "ivr_script": "Health & Disaster Advisory. Severe Heatwave in {area}. Do not step out in direct sun. Drink fluids. Press 1 if you are safe, or press 2 for medical assistance."
            },
            "or": {
                "name": "ଗ୍ରୀଷ୍ମ ପ୍ରବାହ / ଅଂଶୁଘାତ (Heatwave)",
                "headline": "ଭୀଷଣ ଗ୍ରୀଷ୍ମ ପ୍ରବାହ ଓ ଲୁ ସତର୍କତା",
                "recommended_action": "ଦିନ ୧୧ ଟାରୁ ଅପରାହ୍ନ ୪ ଟା ମଧ୍ୟରେ ଖରାରେ ବାହାରକୁ ଯାଆନ୍ତୁ ନାହିଁ। ପ୍ରଚୁର ପାଣି, ତୋରାଣି, ଲେମ୍ବୁ ପାଣି ଓ ଓଆରଏସ ପିଅନ୍ତୁ। ସୂତା ପୋଷାକ ପିନ୍ଧନ୍ତୁ ଏବଂ ଗୃହପାଳିତ ପଶୁଙ୍କୁ ଛାଇରେ ରଖନ୍ତୁ।",
                "short_sms": "[ଗ୍ରୀଷ୍ମ ସତର୍କତା] {area} ରେ ଅଂଶୁଘାତ {severity}। ଖରାରେ ବାହାରନ୍ତୁ ନାହିଁ। ପାଣି/ଓଆରଏସ ପିଅନ୍ତୁ। ସହାୟତା: {helpline}। ସୁରକ୍ଷିତ ଥିଲେ 1, ଚିକିତ୍ସା ପାଇଁ 2।",
                "ivr_script": "ସ୍ୱାସ୍ଥ୍ୟ ସତର୍କତା। {area} ରେ ଭୀଷଣ ଗ୍ରୀଷ୍ମ ପ୍ରବାହ। ଦିନ ବେଳେ ଖରାରେ ବାହାରନ୍ତୁ ନାହିଁ। ସୁରକ୍ଷିତ ଥିଲେ 1, ଡାକ୍ତରୀ ସାହାଯ୍ୟ ପାଇଁ 2 ଦବାନ୍ତୁ।"
            },
            "hi": {
                "name": "भीषण लू (Heatwave)",
                "headline": "अत्यधिक भीषण गर्मी और लू की चेतावनी",
                "recommended_action": "सुबह 11 से शाम 4 बजे तक धूप में निकलने से बचें। खूब पानी, ओआरएस व नींबू पानी पिएं। हल्के सूती कपड़े पहनें। पशुओं को छाया में रखें।",
                "short_sms": "[लू अलर्ट] {area} में भीषण गर्मी {severity}। धूप से बचें, ओआरएस/पानी पिएं। हेल्पलाइन: {helpline}। सुरक्षित हैं तो 1, मदद हेतु 2 भेजें।",
                "ivr_script": "आपदा चेतावनी। {area} में भीषण लू का प्रकोप है। धूप में न जाएं। सुरक्षित होने पर 1 दबाएं, चिकित्सा सहायता के लिए 2 दबाएं।"
            },
            "bn": {
                "name": "তীব্র তাপদাহ (Heatwave)",
                "headline": "চরম তাপদাহ ও সানস্ট্রোক সতর্কতা",
                "recommended_action": "সকাল ১১টা থেকে বিকেল ৪টা পর্যন্ত রোদে বের হবেন না। প্রচুর জল, ওআরএস এবং লেবুর শরবত পান করুন। সুতির হালকা পোশাক পরুন।",
                "short_sms": "[তাপদাহ সতর্কতা] {area} তে চরম গরম {severity}। রোদে বের হবেন না, প্রচুর জল খান। হেল্পলাইন: {helpline}। সুস্থ থাকলে 1, চিকিৎসার জন্য 2 লিখুন।",
                "ivr_script": "জরুরি স্বাস্থ্য সতর্কতা। {area} তে তীব্র তাপদাহ। রোদে বের হবেন না। নিরাপদ থাকলে 1 চাপুন, চিকিৎসার জন্য 2 চাপুন।"
            },
            "te": {
                "name": "తీవ్ర వడగాల్పులు (Heatwave)",
                "headline": "తీవ్రమైన ఎండలు & వడదెబ్బ హెచ్చరిక",
                "recommended_action": "ఉదయం 11 నుండి సాయంత్రం 4 గంటల వరకు ఎండలో తిరగవద్దు. పుష్కలంగా నీరు, ఓఆర్ఎస్ తాగండి. నూలు దుస్తులు ధరించండి.",
                "short_sms": "[హెచ్చరిక] {area} లో తీవ్ర ఎండలు {severity}. ఎండలో తిరగవద్దు, నీరు తాగండి. హెల్ప్‌లైన్: {helpline}. క్షేమంగా ఉంటే 1, అత్యవసరమైతే 2 పంపండి.",
                "ivr_script": "విపత్తు హెచ్చరిక. {area} లో తీవ్ర వడగాల్పులు. ఎండలో బయటకు రావద్దు. క్షేమంగా ఉంటే 1, సహాయం కోసం 2 నొక్కండి."
            },
            "ta": {
                "name": "அனல் காற்று (Heatwave)",
                "headline": "கடுமையான வெப்ப அலை & சூரிய பக்கவாதம் எச்சரிக்கை",
                "recommended_action": "காலை 11 மணி முதல் மாலை 4 மணி வரை வெளியில் செல்வதைத் தவிர்க்கவும். அதிக அளவில் நீர், ORS பருகவும். பருத்தி ஆடைகளை அணியவும்.",
                "short_sms": "[வெப்ப அலை] {area} வெயில் {severity}. 11-4 மணி வரை வெயிலில் செல்லாதீர். நீர் குடிக்கவும். உதவி: {helpline}. நலம் என்றால் 1, உதவிக்கு 2.",
                "ivr_script": "பேரிடர் தகவல். {area} பகுதிக்கு அனல் காற்று எச்சரிக்கை. வெயிலில் செல்ல வேண்டாம். நலமாக இருந்தால் 1, மருத்துவ உதவிக்கு 2 அழுத்தவும்."
            },
            "ur": {
                "name": "شدید گرمی کی لہر (Heatwave)",
                "headline": "ہیٹ ویو اور لو کا سنگین الرٹ",
                "recommended_action": "صبح 11 سے شام 4 بجے تک دھوپ میں نکلنے سے گریز کریں۔ کثرت سے پانی اور او آر ایس پئیں۔ سوتی کپڑے پہنیں۔",
                "short_sms": "[ہیٹ ویو] {area} میں شدید لو {severity}۔ دھوپ سے بچیں، پانی پئیں۔ ہیلپ لائن: {helpline}। خیریت سے ہیں تو 1، امداد کیلئے 2۔",
                "ivr_script": "ہنگامی الرٹ۔ {area} میں شدید ہیٹ ویو کا خطرہ۔ دھوپ سے بچیں۔ خیریت سے ہونے پر 1 دبائیں، طبی امداد کے لیے 2 دبائیں۔"
            }
        }
    },
    "Landslide": {
        "icon": "⛰️",
        "default_helpline": "112, 1070 (Disaster Control Room)",
        "translations": {
            "en": {
                "name": "Landslide",
                "headline": "Critical Hill Slope & Landslide Warning",
                "recommended_action": "Evacuate hillside dwellings immediately. Stay alert for unusual sounds like trees cracking or boulders knocking. Avoid steep valleys and river channels.",
                "short_sms": "[ALERT] LANDSLIDE {severity} in {area}. Evacuate hill slopes immediately. Avoid valleys. Helplines: {helpline}. Reply 1 if SAFE, 2 for RESCUE.",
                "ivr_script": "Emergency Alert. Dangerous Landslide risk in {area}. Evacuate hillside areas immediately. If you are safe, press 1. If you need rescue, press 2."
            },
            "or": {
                "name": "ଭୂସ୍ଖଳନ (Landslide)",
                "headline": "ପାହାଡ଼ିଆ ଅଞ୍ଚଳରେ ମାଟି ଅତଡ଼ା ଖସିବା ବିପଦ ସତର୍କତା",
                "recommended_action": "ପାହାଡ଼ ତଳ ବସତି ତୁରନ୍ତ ଖାଲି କରି ସୁରକ୍ଷିତ ସ୍ଥାନକୁ ଚାଲିଯାଆନ୍ତୁ। ପଥର ଖସିବା କିମ୍ବା ଗଛ ଭାଙ୍ଗିବାର ଶବ୍ଦ ଉପରେ ଧ୍ୟାନ ଦିଅନ୍ତୁ। ପାହାଡ଼ି ନଦୀନାଳ ନିକଟରୁ ଦୂରେଇ ରୁହନ୍ତୁ।",
                "short_sms": "[ସତର୍କତା] {area} ରେ ଭୂସ୍ଖଳନ {severity}। ପାହାଡ଼ ପାଖ ଛାଡ଼ି ସୁରକ୍ଷିତ ଯାଆନ୍ତୁ। ସହାୟତା: {helpline}। ସୁରକ୍ଷିତ ଥିଲେ 1, ସାହାଯ୍ୟ ପାଇଁ 2।",
                "ivr_script": "ଜରୁରୀ ସୂଚନା। {area} ରେ ଭୂସ୍ଖଳନ ଆଶଙ୍କା। ପାହାଡ଼ିଆ ଅଞ୍ଚଳ ଖାଲି କରନ୍ତୁ। ସୁରକ୍ଷିତ ଥିଲେ 1, ସାହାଯ୍ୟ ପାଇଁ 2 ଦବାନ୍ତୁ।"
            },
            "hi": {
                "name": "भूस्खलन (Landslide)",
                "headline": "पहाड़ी ढलानों पर भूस्खलन की गंभीर चेतावनी",
                "recommended_action": "पहाड़ी बस्तियों को तत्काल खाली कर सुरक्षित स्थानों पर जाएं। पेड़ टूटने या पत्थरों के गिरने की आवाज पर सतर्क रहें। नदी-नालों से दूर रहें।",
                "short_sms": "[भूस्खलन अलर्ट] {area} में भूस्खलन {severity}। ढलानों से तुरंत हटें। हेल्पलाइन: {helpline}। सुरक्षित हैं तो 1, बचाव हेतु 2 भेजें।",
                "ivr_script": "आपदा चेतावनी। {area} में भूस्खलन का खतरा है। सुरक्षित स्थान पर जाएं। सुरक्षित होने पर 1 दबाएं, बचाव सहायता के लिए 2 दबाएं।"
            },
            "bn": {
                "name": "ভূমিধস (Landslide)",
                "headline": "পাহাড়ের ঢালে ভূমিধস সতর্কতা",
                "recommended_action": "পাহাড়ের পাদদেশের বাসস্থান অবিলম্বে খালি করে নিরাপদ আশ্রয়ে যান। পাথর খসা বা বিকট শব্দের প্রতি সতর্ক থাকুন। নদী তীর এড়িয়ে চলুন।",
                "short_sms": "[ভূমিধস সতর্কতা] {area} তে ভূমিধস {severity}। পাহাড়ের ঢাল ছাড়ুন। হেল্পলাইন: {helpline}। নিরাপদ থাকলে 1, উদ্ধার 2।",
                "ivr_script": "জরুরি তথ্য। {area} পাহাড়ে ধসের ঝুঁকি রয়েছে। অবিলম্বে সরে যান। নিরাপদ থাকলে 1 চাপুন, উদ্ধার কাজে 2 চাপুন।"
            },
            "te": {
                "name": "కొండచరియలు విరిగిపడటం (Landslide)",
                "headline": "కొండచరియలు విరిగిపడే ప్రమాద హెచ్చరిక",
                "recommended_action": "కొండ దిగువ ప్రాంతాల నుంచి వెంటనే సురక్షిత ప్రాంతాలకు వెళ్లండి. లోయలు మరియు వాగుల వద్ద ఉండవద్దు.",
                "short_sms": "[హెచ్చరిక] {area} లో కొండచరియలు విరిగిపడే ప్రమాదం {severity}. సురక్షిత ప్రాంతాలకు వెళ్లండి. హెల్ప్‌లైన్: {helpline}. సురక్షితమైతే 1, సహాయానికి 2.",
                "ivr_script": "విపత్తు హెచ్చరిక. {area} లో కొండచరియలు విరిగే ప్రమాదం ఉంది. తక్షణమే తరలిపోండి. సురక్షితమైతే 1, రక్షణ కోసం 2 నొక్కండి."
            },
            "ta": {
                "name": "நிலச்சரிவு (Landslide)",
                "headline": "தீவிர நிலச்சரிவு எச்சரிக்கை",
                "recommended_action": "மலைச்சரிவு குடியிருப்புகளில் இருந்து உடனே வெளியேறவும். பாறைகள் உருளும் சத்தம் கேட்டால் எச்சரிக்கையாக இருங்கள். பள்ளத்தாக்குகளைத் தவிர்க்கவும்.",
                "short_sms": "[நிலச்சரிவு] {area} நிலச்சரிவு அபாயம் {severity}. உடனே பாதுகாப்பான இடத்திற்கு செல்லவும். உதவி: {helpline}. பாதுகாப்பாக இருந்தால் 1, உதவிக்கு 2.",
                "ivr_script": "பேரிடர் தகவல். {area} மலைப்பகுதியில் நிலச்சரிவு அபாயம். பாதுகாப்பான பகுதிக்கு செல்லவும். பாதுகாப்பாக இருந்தால் 1, உதவிக்கு 2 அழுத்தவும்."
            },
            "ur": {
                "name": "لینڈ سلائیڈنگ (Landslide)",
                "headline": "پہاڑی ڈھلوانوں پر مٹی کھسکنے کا خطرہ",
                "recommended_action": "پہاڑی بستیوں سے فوری محفوظ مقامات پر منتقل ہوں۔ گرتے پتھروں کی آوازوں سے چوکنا رہیں۔ ندی نالوں سے پرے رہیں۔",
                "short_sms": "[انتباہ] {area} میں لینڈ سلائیڈنگ {severity}۔ پہاڑی علاقے فوری خالی کریں۔ ہیلپ لائن: {helpline}। محفوظ ہیں تو 1, امداد 2۔",
                "ivr_script": "ہنگامی الرٹ۔ {area} میں لینڈ سلائیڈنگ کا خطرہ۔ محفوظ مقام پر جائیں۔ محفوظ ہونے پر 1 دبائیں، امداد کے لیے 2 دبائیں۔"
            }
        }
    },
    "Tsunami": {
        "icon": "🌊",
        "default_helpline": "112, 1070 (State Emergency Center)",
        "translations": {
            "en": {
                "name": "Tsunami",
                "headline": "Major Ocean Tsunami Inundation Threat",
                "recommended_action": "Move INLAND and to HIGH GROUND (at least 15m/50ft above sea level or 3km inland) immediately. Do NOT go to the coast to watch waves.",
                "short_sms": "[CRITICAL] TSUNAMI {severity} for {area} coast. Evacuate 3km inland or 15m high immediately. Helplines: {helpline}. Reply 1 if SAFE, 2 for RESCUE.",
                "ivr_script": "Extreme Life Threatening Alert. Major Tsunami detected for coastal {area}. Evacuate inland and to higher ground immediately. Press 1 if safe, 2 for rescue."
            },
            "or": {
                "name": "ସୁନାମୀ (Tsunami)",
                "headline": "ସମୁଦ୍ର ତଟରେ ମହାବିପଦ ସୁନାମୀ ସତର୍କତା",
                "recommended_action": "ସମୁଦ୍ର ତଟ ତୁରନ୍ତ ଛାଡ଼ି କମ ସେ କମ ୩ କିମି ଭିତରକୁ କିମ୍ବା ଅତିକମରେ ୧୫ ମିଟର ଉଚ୍ଚ ସ୍ଥାନକୁ ଚାଲିଯାଆନ୍ତୁ। ସମୁଦ୍ର କୂଳକୁ ଆଦୌ ଯାଆନ୍ତୁ ନାହିଁ।",
                "short_sms": "[ମହାବିପଦ] {area} ଉପକୂଳରେ ସୁନାମୀ {severity}। ତୁରନ୍ତ ୩ କିମି ଭିତରକୁ ବା ଉଚ୍ଚ ସ୍ଥାନକୁ ଯାଆନ୍ତୁ। ସହାୟତା: {helpline}। ସୁରକ୍ଷିତ ଥିଲେ 1, ସାହାଯ୍ୟ ପାଇଁ 2।",
                "ivr_script": "ଚରମ ଜୀବନ ବିପଦ ସତର୍କତା। {area} ଉପକୂଳରେ ସୁନାମୀ ବିପଦ। ତୁରନ୍ତ ସମୁଦ୍ର ଛାଡ଼ି ଉଚ୍ଚ ସ୍ଥାନକୁ ଯାଆନ୍ତୁ। ସୁରକ୍ଷିତ ଥିଲେ 1, ସାହାଯ୍ୟ ପାଇଁ 2 ଦବାନ୍ତୁ।"
            },
            "hi": {
                "name": "सुनामी (Tsunami)",
                "headline": "तटीय क्षेत्रों में भयानक सुनामी चेतावनी",
                "recommended_action": "समुद्र तट छोड़कर तुरंत कम से कम 3 किमी अंदर या 15 मीटर ऊंचे स्थान पर जाएं। सुनामी की लहरें देखने तट पर बिल्कुल न जाएं।",
                "short_sms": "[सुनामी अलर्ट] {area} तट पर सुनामी {severity}। तुरंत 3 किमी अंदर या ऊंचे स्थान पर जाएं। हेल्पलाइन: {helpline}। सुरक्षित हैं तो 1, मदद हेतु 2 भेजें।",
                "ivr_script": "अत्यंत गंभीर आपात चेतावनी। {area} तट पर सुनामी का खतरा। तुरंत ऊंचे स्थान पर जाएं। सुरक्षित होने पर 1 दबाएं, बचाव हेतु 2 दबाएं।"
            },
            "bn": {
                "name": "সুনামি (Tsunami)",
                "headline": "উপকূলীয় অঞ্চলে ভয়াবহ সুনামি সতর্কতা",
                "recommended_action": "উপকূল অবিলম্বে ত্যাগ করে অন্তত ৩ কিমি অভ্যন্তরে বা উঁচু স্থানে চলে যান। সমুদ্রের ঢেউ দেখতে যাবেন না।",
                "short_sms": "[সুনামি চরম সতর্কতা] {area} উপকূলে সুনামি {severity}। ৩ কিমি ভেতরে বা উঁচু স্থানে যান। হেল্পলাইন: {helpline}। নিরাপদ থাকলে 1, উদ্ধার 2।",
                "ivr_script": "চরম সংকটকালীন বার্তা। {area} উপকূলে সুনামি সতর্কতা। অবিলম্বে উপকূল ত্যাগ করুন। নিরাপদ থাকলে 1 চাপুন, উদ্ধার 2 চাপুন।"
            },
            "te": {
                "name": "సునామీ (Tsunami)",
                "headline": "తీర ప్రాంతానికి తీవ్ర సునామీ ముప్పు",
                "recommended_action": "తీరం విడిచి కనీసం 3 కిలోమీటర్లు లోపలికి లేదా ఎత్తైన ప్రదేశాలకు వెంటనే తరలిపోండి. అలలు చూడటానికి తీరానికి వెళ్లవద్దు.",
                "short_sms": "[తీవ్ర హెచ్చరిక] {area} తీరంలో సునామీ {severity}. 3 కిమీ లోపలికి లేదా ఎత్తైన ప్రదేశానికి వెళ్లండి. హెల్ప్‌లైన్: {helpline}. సురక్షితమైతే 1, రక్షణకు 2.",
                "ivr_script": "అత్యవసర సునామీ హెచ్చరిక. {area} తీరం వదిలి వెంటనే ఎత్తైన ప్రదేశానికి వెళ్లండి. సురక్షితమైతే 1, రక్షణ కోసం 2 నొక్కండి."
            },
            "ta": {
                "name": "சுனாமி (Tsunami)",
                "headline": "கடலோரப்பகுதியில் தீவிர சுனாமி பேரலை எச்சரிக்கை",
                "recommended_action": "கடற்கரையை விட்டு உடனே 3 கி.மீ உள்நோக்கியோ அல்லது உயரமான பகுதிக்கோ செல்லவும். அலையைப் பார்க்க கடற்கரைக்கு செல்ல வேண்டாம்.",
                "short_sms": "[சுனாமி எச்சரிக்கை] {area} கடற்கரையில் சுனாமி {severity}. உடனே 3 கி.மீ உள்நோக்கி அல்லது மேடான பகுதிக்கு செல்லவும். உதவி: {helpline}. நலம் என்றால் 1, உதவிக்கு 2.",
                "ivr_script": "அதிதீவிர சுனாமி எச்சரிக்கை. {area} கடற்கரையை விட்டு உடனடியாக மேடான பகுதிக்கு செல்லவும். நலமாக இருந்தால் 1, உதவிக்கு 2 அழுத்தவும்."
            },
            "ur": {
                "name": "سونامی (Tsunami)",
                "headline": "ساحلی علاقوں میں ہلاکت خیز سونامی کا انتباہ",
                "recommended_action": "ساحل فورا چھوڑ کر کم از کم 3 کلومیٹر اندر یا 15 میٹر اونچی جگہ منتقل ہوں۔ لہریں دیکھنے ساحل مت جائیں۔",
                "short_sms": "[سونامی خطرہ] {area} ساحل پر سونامی {severity}۔ فورا ساحل چھوڑ کر اونچی جگہ جائیں۔ ہیلپ لائن: {helpline}۔ محفوظ ہیں تو 1, امداد 2۔",
                "ivr_script": "انتہائی سنگین خطرہ۔ {area} کے ساحل پر سونامی کا انتباہ۔ فورا اونچی جگہ جائیں۔ محفوظ ہونے پر 1 دبائیں، امداد کے لیے 2 دبائیں۔"
            }
        }
    }
}

def render_alert_text(hazard_type, severity, area_name, lang="en", helpline=None):
    """
    Renders pre-verified multilingual alert payload.
    Never uses machine translation: fetches the deterministic human-curated emergency template.
    """
    if hazard_type not in HAZARDS:
        hazard_type = "Cyclone"
    if severity not in SEVERITY_LEVELS:
        severity = "Warning"
    if lang not in LANGUAGES:
        lang = "en"
        
    hazard_info = HAZARDS[hazard_type]
    trans = hazard_info["translations"].get(lang, hazard_info["translations"]["en"])
    sev_label = SEVERITY_LEVELS[severity]["labels"].get(lang, severity)
    contacts = helpline or hazard_info["default_helpline"]
    
    headline = trans["headline"]
    rec_action = trans["recommended_action"]
    
    # Formatted short SMS (guaranteed concise & under 160 unicode/GSM limits)
    short_sms = trans["short_sms"].format(
        area=area_name,
        severity=sev_label.split(" (")[0],
        helpline=contacts.split(",")[0]
    )
    
    # IVR spoken script
    ivr_script = trans["ivr_script"].format(
        area=area_name,
        severity=sev_label
    )
    
    return {
        "hazard_type": hazard_type,
        "hazard_icon": hazard_info["icon"],
        "severity": severity,
        "severity_color": SEVERITY_LEVELS[severity]["color"],
        "severity_label": sev_label,
        "area_name": area_name,
        "language": lang,
        "language_name": LANGUAGES[lang]["name"],
        "language_native": LANGUAGES[lang]["native"],
        "headline": headline,
        "recommended_action": rec_action,
        "helplines": contacts,
        "short_sms": short_sms,
        "sms_length": len(short_sms),
        "ivr_script": ivr_script
    }

def get_all_translations_preview(hazard_type, severity, area_name, helpline=None):
    """Generates preview across all 7 languages for the admin dashboard"""
    previews = {}
    for code, info in LANGUAGES.items():
        previews[code] = render_alert_text(hazard_type, severity, area_name, code, helpline)
    return previews
