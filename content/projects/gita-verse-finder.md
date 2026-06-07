---
title: "Gita Verse Finder"
tags:
  - philosophy
  - hinduism
  - interactive
description: Select a theme and receive a verse from the Bhagavad Gita. Covers duty, grief, action, fear, love, anger, impermanence, the self, wisdom, family, attachment, and more.
---

<div id="gita-root">

<div class="gita-intro">
<p>Select a theme. A verse will appear.</p>
</div>

<div class="gita-topics" id="gita-topics"></div>

<div id="gita-verse-area"></div>

</div>

<script>
(function () {

var VERSES = [
  // ── DUTY ──────────────────────────────────────────────────────────────────
  {
    ref: "2.47",
    sanskrit: "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।\nमा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥",
    transliteration: "Karmaṇy evādhikāras te mā phaleṣu kadācana\nmā karma-phala-hetur bhūr mā te saṅgo 'stv akarmaṇi",
    translation: "You have a right to perform your prescribed duties, but you are not entitled to the fruits of your actions. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.",
    topics: ["duty", "action", "attachment"]
  },
  {
    ref: "3.35",
    sanskrit: "श्रेयान्स्वधर्मो विगुणः परधर्मात्स्वनुष्ठितात्।\nस्वधर्मे निधनं श्रेयः परधर्मो भयावहः॥",
    transliteration: "Śreyān sva-dharmo viguṇaḥ para-dharmāt sv-anuṣṭhitāt\nsva-dharme nidhanaṁ śreyaḥ para-dharmo bhayāvahaḥ",
    translation: "It is far better to discharge one's prescribed duties, even though they may be imperfectly performed, than to perform the duties of another. Destruction in the course of one's own duty is better than engaging in another's duty, for following another's path is dangerous.",
    topics: ["duty", "purpose", "fear"]
  },
  {
    ref: "4.7",
    sanskrit: "यदा यदा हि धर्मस्य ग्लानिर्भवति भारत।\nअभ्युत्थानमधर्मस्य तदात्मानं सृजाम्यहम्॥",
    transliteration: "Yadā yadā hi dharmasya glānir bhavati Bhārata\nabhyutthānam adharmasya tadātmānaṁ sṛjāmy aham",
    translation: "Whenever and wherever there is a decline in righteousness, O Arjuna, and a predominant rise of irreligion — at that time I manifest myself.",
    topics: ["duty", "purpose", "action"]
  },
  {
    ref: "18.66",
    sanskrit: "सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज।\nअहं त्वा सर्वपापेभ्यो मोक्षयिष्यामि मा शुचः॥",
    transliteration: "Sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja\nahaṁ tvāṁ sarva-pāpebhyo mokṣayiṣyāmi mā śucaḥ",
    translation: "Abandon all varieties of duty and surrender unto me alone. I shall deliver you from all sinful reactions. Do not fear.",
    topics: ["duty", "surrender", "fear", "love"]
  },

  // ── GRIEF ─────────────────────────────────────────────────────────────────
  {
    ref: "2.11",
    sanskrit: "अशोच्यानन्वशोचस्त्वं प्रज्ञावादांश्च भाषसे।\nगतासूनगतासूंश्च नानुशोचन्ति पण्डिताः॥",
    transliteration: "Aśocyān anvaśocas tvaṁ prajñā-vādāṁś ca bhāṣase\ngatāsūn agatāsūṁś ca nānuśocanti paṇḍitāḥ",
    translation: "You grieve for those who are not to be grieved for, yet you speak words of wisdom. The wise grieve neither for the living nor for the dead.",
    topics: ["grief", "wisdom", "impermanence", "death"]
  },
  {
    ref: "2.27",
    sanskrit: "जातस्य हि ध्रुवो मृत्युर्ध्रुवं जन्म मृतस्य च।\nतस्मादपरिहार्येऽर्थे न त्वं शोचितुमर्हसि॥",
    transliteration: "Jātasya hi dhruvo mṛtyur dhruvaṁ janma mṛtasya ca\ntasmād aparihārye 'rthe na tvaṁ śocitum arhasi",
    translation: "Death is certain for the born, and birth is certain for the dead. You should not grieve over the inevitable.",
    topics: ["grief", "death", "impermanence"]
  },
  {
    ref: "2.3",
    sanskrit: "क्लैब्यं मा स्म गमः पार्थ नैतत्त्वय्युपपद्यते।\nक्षुद्रं हृदयदौर्बल्यं त्यक्त्वोत्तिष्ठ परन्तप॥",
    transliteration: "Klaibyaṁ mā sma gamaḥ Pārtha naitat tvayy upapadyate\nkṣudraṁ hṛdaya-daurbalyaṁ tyaktvottiṣṭha parantapa",
    translation: "Do not yield to this degrading impotence, O Arjuna. It does not become you. Give up such faint-heartedness and arise.",
    topics: ["grief", "courage", "fear", "action"]
  },

  // ── ACTION ────────────────────────────────────────────────────────────────
  {
    ref: "2.48",
    sanskrit: "योगस्थः कुरु कर्माणि सङ्गं त्यक्त्वा धनञ्जय।\nसिद्ध्यसिद्ध्योः समो भूत्वा समत्वं योग उच्यते॥",
    transliteration: "Yoga-sthaḥ kuru karmāṇi saṅgaṁ tyaktvā Dhanañjaya\nsiddhy-asiddhyoḥ samo bhūtvā samatvaṁ yoga ucyate",
    translation: "Perform your duty equipoised, O Arjuna, abandoning all attachment to success or failure. Such equanimity is called yoga.",
    topics: ["action", "attachment", "equanimity"]
  },
  {
    ref: "3.19",
    sanskrit: "तस्मादसक्तः सततं कार्यं कर्म समाचर।\nअसक्तो ह्याचरन्कर्म परमाप्नोति पूरुषः॥",
    transliteration: "Tasmād asaktaḥ satataṁ kāryaṁ karma samācara\nasakto hy ācaran karma param āpnoti pūruṣaḥ",
    translation: "Therefore, without attachment, perform always the work that has to be done, for by performing action without attachment, one attains the Supreme.",
    topics: ["action", "attachment", "duty"]
  },
  {
    ref: "4.18",
    sanskrit: "कर्मण्यकर्म यः पश्येदकर्मणि च कर्म यः।\nस बुद्धिमान्मनुष्येषु स युक्तः कृत्स्नकर्मकृत्॥",
    transliteration: "Karmaṇy akarma yaḥ paśyed akarmaṇi ca karma yaḥ\nsa buddhimān manuṣyeṣu sa yuktaḥ kṛtsna-karma-kṛt",
    translation: "One who sees inaction in action, and action in inaction, is intelligent among men, and is in the transcendental position, though engaged in all sorts of activities.",
    topics: ["action", "wisdom", "self"]
  },

  // ── FEAR ──────────────────────────────────────────────────────────────────
  {
    ref: "2.14",
    sanskrit: "मात्रास्पर्शास्तु कौन्तेय शीतोष्णसुखदुःखदाः।\nआगमापायिनोऽनित्यास्तांस्तितिक्षस्व भारत॥",
    transliteration: "Mātrā-sparśās tu Kaunteya śītoṣṇa-sukha-duḥkha-dāḥ\nāgamāpāyino 'nityās tāṁs titikṣasva Bhārata",
    translation: "O son of Kunti, the nonpermanent appearance of happiness and distress, and their disappearance in due course, are like the appearance and disappearance of winter and summer seasons. They arise from sense perception, and one must learn to tolerate them without being disturbed.",
    topics: ["fear", "impermanence", "equanimity"]
  },
  {
    ref: "4.40",
    sanskrit: "अज्ञश्चाश्रद्दधानश्च संशयात्मा विनश्यति।\nनायं लोकोऽस्ति न परो न सुखं संशयात्मनः॥",
    transliteration: "Ajñaś cāśraddadhānaś ca saṁśayātmā vinaśyati\nnāyaṁ loko 'sti na paro na sukhaṁ saṁśayātmanaḥ",
    translation: "But ignorant and faithless persons who doubt the revealed scriptures do not attain God consciousness. For the doubting soul there is happiness neither in this world nor the next.",
    topics: ["fear", "wisdom", "doubt"]
  },

  // ── LOVE & DEVOTION ───────────────────────────────────────────────────────
  {
    ref: "9.22",
    sanskrit: "अनन्याश्चिन्तयन्तो मां ये जनाः पर्युपासते।\nतेषां नित्याभियुक्तानां योगक्षेमं वहाम्यहम्॥",
    transliteration: "Ananyāś cintayanto māṁ ye janāḥ paryupāsate\nteṣāṁ nityābhiyuktānāṁ yoga-kṣemaṁ vahāmy aham",
    translation: "For those who worship me with devotion, meditating on my transcendental form, I carry what they lack and preserve what they have.",
    topics: ["love", "devotion", "surrender"]
  },
  {
    ref: "12.13",
    sanskrit: "अद्वेष्टा सर्वभूतानां मैत्रः करुण एव च।\nनिर्ममो निरहङ्कारः समदुःखसुखः क्षमी॥",
    transliteration: "Adveṣṭā sarva-bhūtānāṁ maitraḥ karuṇa eva ca\nnirmamo nirahaṅkāraḥ sama-duḥkha-sukhaḥ kṣamī",
    translation: "One who is not envious but is a kind friend to all living beings, who does not think himself a proprietor and is free from false ego, who is equal in happiness and distress, and is forgiving — he is very dear to me.",
    topics: ["love", "relationships", "ego", "wisdom"]
  },
  {
    ref: "18.65",
    sanskrit: "मन्मना भव मद्भक्तो मद्याजी मां नमस्कुरु।\nमामेवैष्यसि सत्यं ते प्रतिजाने प्रियोऽसि मे॥",
    transliteration: "Man-manā bhava mad-bhakto mad-yājī māṁ namaskuru\nmām evaiṣyasi satyaṁ te pratijāne priyo 'si me",
    translation: "Always think of me, become my devotee, worship me and offer your homage unto me. Thus you will come to me without fail. I promise you this because you are my very dear friend.",
    topics: ["love", "devotion", "surrender"]
  },

  // ── ANGER & EGO ───────────────────────────────────────────────────────────
  {
    ref: "2.62",
    sanskrit: "ध्यायतो विषयान्पुंसः सङ्गस्तेषूपजायते।\nसङ्गात्सञ्जायते कामः कामात्क्रोधोऽभिजायते॥",
    transliteration: "Dhyāyato viṣayān puṁsaḥ saṅgas teṣūpajāyate\nsaṅgāt sañjāyate kāmaḥ kāmāt krodho 'bhijāyate",
    translation: "While contemplating the objects of the senses, a person develops attachment for them, and from such attachment lust develops, and from lust anger arises.",
    topics: ["anger", "desire", "attachment"]
  },
  {
    ref: "2.63",
    sanskrit: "क्रोधाद्भवति सम्मोहः सम्मोहात्स्मृतिविभ्रमः।\nस्मृतिभ्रंशाद्बुद्धिनाशो बुद्धिनाशात्प्रणश्यति॥",
    transliteration: "Krodhād bhavati sammohaḥ sammohāt smṛti-vibhramaḥ\nsmṛti-bhraṁśād buddhi-nāśo buddhi-nāśāt praṇaśyati",
    translation: "From anger, delusion arises, and from delusion bewilderment of memory. When memory is bewildered, intelligence is lost, and when intelligence is lost, one falls down again into the material pool.",
    topics: ["anger", "wisdom", "desire"]
  },
  {
    ref: "3.37",
    sanskrit: "काम एष क्रोध एष रजोगुणसमुद्भवः।\nमहाशनो महापाप्मा विद्ध्येनमिह वैरिणम्॥",
    transliteration: "Kāma eṣa krodha eṣa rajo-guṇa-samudbhavaḥ\nmahāśano mahā-pāpmā viddhy enam iha vairiṇam",
    translation: "It is lust only, Arjuna, which is born of contact with the material modes of passion and later transformed into wrath, and which is the all-devouring, sinful enemy of this world.",
    topics: ["anger", "desire", "ego"]
  },
  {
    ref: "16.21",
    sanskrit: "त्रिविधं नरकस्येदं द्वारं नाशनमात्मनः।\nकामः क्रोधस्तथा लोभस्तस्मादेतत्त्रयं त्यजेत्॥",
    transliteration: "Tri-vidhaṁ narakasyedaṁ dvāraṁ nāśanam ātmanaḥ\nkāmaḥ krodhas tathā lobhas tasmād etat trayaṁ tyajet",
    translation: "There are three gates leading to the hell of self-destruction for the soul — lust, anger, and greed. Therefore, all persons of discernment should give up these three.",
    topics: ["anger", "desire", "ego", "wisdom"]
  },

  // ── IMPERMANENCE & DEATH ──────────────────────────────────────────────────
  {
    ref: "2.19",
    sanskrit: "य एनं वेत्ति हन्तारं यश्चैनं मन्यते हतम्।\nउभौ तौ न विजानीतो नायं हन्ति न हन्यते॥",
    transliteration: "Ya enaṁ vetti hantāraṁ yaś cainaṁ manyate hatam\nubhau tau na vijānīto nāyaṁ hanti na hanyate",
    translation: "He who thinks that the soul is a slayer and he who thinks that the soul is slain — both of them are in ignorance. The soul neither slays, nor is it slain.",
    topics: ["impermanence", "death", "self"]
  },
  {
    ref: "2.20",
    sanskrit: "न जायते म्रियते वा कदाचिन्नायं भूत्वा भविता वा न भूयः।\nअजो नित्यः शाश्वतोऽयं पुराणो न हन्यते हन्यमाने शरीरे॥",
    transliteration: "Na jāyate mriyate vā kadācin nāyaṁ bhūtvā bhavitā vā na bhūyaḥ\najo nityaḥ śāśvato 'yaṁ purāṇo na hanyate hanyamāne śarīre",
    translation: "The soul is never born nor dies at any time. It has not come into being, does not come into being, and will not come into being. It is unborn, eternal, ever-existing, and primeval. It is not slain when the body is slain.",
    topics: ["impermanence", "death", "self", "grief"]
  },
  {
    ref: "2.22",
    sanskrit: "वासांसि जीर्णानि यथा विहाय नवानि गृह्णाति नरोऽपराणि।\nतथा शरीराणि विहाय जीर्णान्यन्यानि संयाति नवानि देही॥",
    transliteration: "Vāsāṁsi jīrṇāni yathā vihāya navāni gṛhṇāti naro 'parāṇi\ntathā śarīrāṇi vihāya jīrṇāny anyāni saṁyāti navāni dehī",
    translation: "As a person puts on new garments, giving up old ones, the soul similarly accepts new material bodies, giving up the old and useless ones.",
    topics: ["impermanence", "death", "self"]
  },

  // ── THE SELF ──────────────────────────────────────────────────────────────
  {
    ref: "6.5",
    sanskrit: "उद्धरेदात्मनात्मानं नात्मानमवसादयेत्।\nआत्मैव ह्यात्मनो बन्धुरात्मैव रिपुरात्मनः॥",
    transliteration: "Uddhared ātmanātmānaṁ nātmānam avasādayet\nātmaiva hy ātmano bandhur ātmaiva ripur ātmanaḥ",
    translation: "A man must elevate himself by his own mind, not degrade himself. The mind is the friend of the conditioned soul, and his enemy as well.",
    topics: ["self", "wisdom", "purpose"]
  },
  {
    ref: "3.27",
    sanskrit: "प्रकृतेः क्रियमाणानि गुणैः कर्माणि सर्वशः।\nअहङ्कारविमूढात्मा कर्ताहमिति मन्यते॥",
    transliteration: "Prakṛteḥ kriyamāṇāni guṇaiḥ karmāṇi sarvaśaḥ\nahaṅkāra-vimūḍhātmā kartāham iti manyate",
    translation: "The bewildered spirit thinks itself to be the doer of activities that are in actuality carried out by the three modes of material nature.",
    topics: ["self", "ego", "action"]
  },
  {
    ref: "13.27",
    sanskrit: "समं पश्यन्हि सर्वत्र समवस्थितमीश्वरम्।\nन हिनस्त्यात्मनात्मानं ततो याति परां गतिम्॥",
    transliteration: "Samaṁ paśyan hi sarvatra samavasthitam īśvaram\nna hinasty ātmanātmānaṁ tato yāti parāṁ gatim",
    translation: "One who sees the Supersoul equally present everywhere, in every living being, does not degrade himself by his mind. He thus approaches the transcendental destination.",
    topics: ["self", "wisdom", "equanimity"]
  },
  {
    ref: "6.19",
    sanskrit: "यथा दीपो निवातस्थो नेङ्गते सोपमा स्मृता।\nयोगिनो यतचित्तस्य युञ्जतो योगमात्मनः॥",
    transliteration: "Yathā dīpo nivāta-stho neṅgate sopamā smṛtā\nyogino yata-cittasya yuñjato yogam ātmanaḥ",
    translation: "As a lamp in a windless place does not flicker, so the disciplined mind of a yogi remains steady in the practice of meditation on the self.",
    topics: ["self", "wisdom", "equanimity"]
  },

  // ── WISDOM & KNOWLEDGE ────────────────────────────────────────────────────
  {
    ref: "5.18",
    sanskrit: "विद्याविनयसम्पन्ने ब्राह्मणे गवि हस्तिनि।\nशुनि चैव श्वपाके च पण्डिताः समदर्शिनः॥",
    transliteration: "Vidyā-vinaya-sampanne brāhmaṇe gavi hastini\nśuni caiva śva-pāke ca paṇḍitāḥ sama-darśinaḥ",
    translation: "The wise see with equal vision a learned and gentle Brahmin, a cow, an elephant, a dog, and a dog-eater.",
    topics: ["wisdom", "equanimity", "self"]
  },
  {
    ref: "4.38",
    sanskrit: "न हि ज्ञानेन सदृशं पवित्रमिह विद्यते।\nतत्स्वयं योगसंसिद्धः कालेनात्मनि विन्दति॥",
    transliteration: "Na hi jñānena sadṛśaṁ pavitram iha vidyate\ntat svayaṁ yoga-saṁsiddhaḥ kālenātmani vindati",
    translation: "In this world there is nothing so sublime and pure as transcendental knowledge. Such knowledge is the mature fruit of all mysticism, and one who has become accomplished in the practice of devotional service enjoys this knowledge within himself in due course of time.",
    topics: ["wisdom", "knowledge", "action"]
  },
  {
    ref: "10.20",
    sanskrit: "अहमात्मा गुडाकेश सर्वभूताशयस्थितः।\nअहमादिश्च मध्यं च भूतानामन्त एव च॥",
    transliteration: "Aham ātmā Guḍākeśa sarva-bhūtāśaya-sthitaḥ\naham ādiś ca madhyaṁ ca bhūtānām anta eva ca",
    translation: "I am the Self, O Gudakesha, seated in the hearts of all creatures. I am the beginning, the middle and the end of all beings.",
    topics: ["wisdom", "self", "love"]
  },

  // ── FAMILY & RELATIONSHIPS ────────────────────────────────────────────────
  {
    ref: "1.28",
    sanskrit: "दृष्ट्वेमं स्वजनं कृष्ण युयुत्सुं समुपस्थितम्।\nसीदन्ति मम गात्राणि मुखं च परिशुष्यति॥",
    transliteration: "Dṛṣṭvemaṁ sva-janaṁ Kṛṣṇa yuyutsuṁ samupasthitam\nsīdanti mama gātrāṇi mukhaṁ ca pariśuṣyati",
    translation: "Arjuna said: My dear Krishna, seeing my friends and relatives present before me in such a fighting spirit, I feel the limbs of my body quivering and my mouth drying up.",
    topics: ["family", "grief", "relationships", "fear"]
  },
  {
    ref: "1.37",
    sanskrit: "यद्यप्येते न पश्यन्ति लोभोपहतचेतसः।\nकुलक्षयकृतं दोषं मित्रद्रोहे च पातकम्॥",
    transliteration: "Yady apy ete na paśyanti lobhopahata-cetasaḥ\nkula-kṣaya-kṛtaṁ doṣaṁ mitra-drohe ca pātakam",
    translation: "O Janardana, although these men, their hearts overtaken by greed, see no fault in killing one's family or quarrelling with friends, why should we, who can see the crime in destroying a family, engage in these acts of sin?",
    topics: ["family", "relationships", "duty", "grief"]
  },
  {
    ref: "11.55",
    sanskrit: "मत्कर्मकृन्मत्परमो मद्भक्तः सङ्गवर्जितः।\nनिर्वैरः सर्वभूतेषु यः स मामेति पाण्डव॥",
    transliteration: "Mat-karma-kṛn mat-paramo mad-bhaktaḥ saṅga-varjitaḥ\nnirvairaḥ sarva-bhūteṣu yaḥ sa mām eti Pāṇḍava",
    translation: "My dear Arjuna, one who engages in my pure devotional service, free from the contaminations of previous activities and mental speculation, who works for me, who makes me the supreme goal of his life, and who is friendly to every living being — he certainly comes to me.",
    topics: ["relationships", "love", "action", "purpose"]
  },

  // ── ATTACHMENT & DESIRE ───────────────────────────────────────────────────
  {
    ref: "3.21",
    sanskrit: "यद्यदाचरति श्रेष्ठस्तत्तदेवेतरो जनः।\nस यत्प्रमाणं कुरुते लोकस्तदनुवर्तते॥",
    transliteration: "Yad yad ācarati śreṣṭhas tat tad evetaro janaḥ\nsa yat pramāṇaṁ kurute lokas tad anuvartate",
    translation: "Whatever action a great man performs, common men follow. And whatever standards he sets by exemplary acts, all the world pursues.",
    topics: ["attachment", "action", "relationships"]
  },
  {
    ref: "6.35",
    sanskrit: "असंशयं महाबाहो मनो दुर्निग्रहं चलम्।\nअभ्यासेन तु कौन्तेय वैराग्येण च गृह्यते॥",
    transliteration: "Asaṁśayaṁ mahā-bāho mano durnigrahaṁ calam\nabhyāsena tu Kaunteya vairāgyeṇa ca gṛhyate",
    translation: "Lord Krishna said: O mighty-armed Arjuna, the mind is undoubtedly restless and difficult to restrain, but it is brought under control by constant practice and by non-attachment.",
    topics: ["attachment", "desire", "self", "wisdom"]
  },
  {
    ref: "3.43",
    sanskrit: "एवं बुद्धेः परं बुद्ध्वा संस्तभ्यात्मानमात्मना।\nजहि शत्रुं महाबाहो कामरूपं दुरासदम्॥",
    transliteration: "Evaṁ buddheḥ paraṁ buddhvā saṁstabhyātmānam ātmanā\njahi śatruṁ mahā-bāho kāma-rūpaṁ durāsadam",
    translation: "Thus knowing oneself to be transcendental to material senses, mind, and intelligence, O mighty-armed Arjuna, one should steady the mind by deliberate spiritual intelligence and thus — by spiritual strength — conquer this insatiable enemy known as lust.",
    topics: ["attachment", "desire", "self", "action"]
  },

  // ── PURPOSE & MEANING ─────────────────────────────────────────────────────
  {
    ref: "4.8",
    sanskrit: "परित्राणाय साधूनां विनाशाय च दुष्कृताम्।\nधर्मसंस्थापनार्थाय सम्भवामि युगे युगे॥",
    transliteration: "Paritrāṇāya sādhūnāṁ vināśāya ca duṣkṛtām\ndharma-saṁsthāpanārthāya sambhavāmi yuge yuge",
    translation: "To deliver the pious and to annihilate the miscreants, as well as to reestablish the principles of righteousness, I advent myself millennium after millennium.",
    topics: ["purpose", "duty", "action"]
  },
  {
    ref: "18.63",
    sanskrit: "इति ते ज्ञानमाख्यातं गुह्याद्गुह्यतरं मया।\nविमृश्यैतदशेषेण यथेच्छसि तथा कुरु॥",
    transliteration: "Iti te jñānam ākhyātaṁ guhyād guhyataraṁ mayā\nvimṛśyaitad aśeṣeṇa yathecchasi tathā kuru",
    translation: "Thus I have explained to you the most confidential of all knowledge. Deliberate on this fully, and then do what you wish to do.",
    topics: ["purpose", "wisdom", "action", "self"]
  },
  {
    ref: "9.2",
    sanskrit: "राजविद्या राजगुह्यं पवित्रमिदमुत्तमम्।\nप्रत्यक्षावगमं धर्म्यं सुसुखं कर्तुमव्ययम्॥",
    transliteration: "Rāja-vidyā rāja-guhyaṁ pavitram idam uttamam\npratyakṣāvagamaṁ dharmyaṁ su-sukhaṁ kartum avyayam",
    translation: "This knowledge is the king of all education, the most secret of all secrets. It is the purest knowledge, and because it gives direct perception of the self by realisation, it is the perfection of religion.",
    topics: ["purpose", "wisdom", "knowledge"]
  },

  // ── EQUANIMITY ────────────────────────────────────────────────────────────
  {
    ref: "5.20",
    sanskrit: "न प्रहृष्येत्प्रियं प्राप्य नोद्विजेत्प्राप्य चाप्रियम्।\nस्थिरबुद्धिरसम्मूढो ब्रह्मविद्ब्रह्मणि स्थितः॥",
    transliteration: "Na prahṛṣyet priyaṁ prāpya nodvijet prāpya cāpriyam\nsthira-buddhir asammūḍho brahma-vid brahmaṇi sthitaḥ",
    translation: "A person who neither rejoices upon achieving something pleasant nor laments upon obtaining something unpleasant, who is self-intelligent, unbewildered, and who knows the science of God, is to be understood as already situated in transcendence.",
    topics: ["equanimity", "wisdom", "self", "impermanence"]
  },
  {
    ref: "12.17",
    sanskrit: "यो न हृष्यति न द्वेष्टि न शोचति न काङ्क्षति।\nशुभाशुभपरित्यागी भक्तिमान्यः स मे प्रियः॥",
    transliteration: "Yo na hṛṣyati na dveṣṭi na śocati na kāṅkṣati\nśubhāśubha-parityāgī bhaktimān yaḥ sa me priyaḥ",
    translation: "One who neither rejoices nor grieves, who neither laments nor desires, and who renounces both auspicious and inauspicious things — such a devotee is very dear to me.",
    topics: ["equanimity", "love", "attachment", "grief"]
  }
];

var TOPICS = [
  { id: "duty",         label: "Duty" },
  { id: "grief",        label: "Grief & Loss" },
  { id: "action",       label: "Action & Work" },
  { id: "fear",         label: "Fear & Courage" },
  { id: "love",         label: "Love & Devotion" },
  { id: "anger",        label: "Anger & Ego" },
  { id: "impermanence", label: "Impermanence & Death" },
  { id: "self",         label: "The Self" },
  { id: "wisdom",       label: "Wisdom & Knowledge" },
  { id: "family",       label: "Family & Relationships" },
  { id: "attachment",   label: "Attachment & Desire" },
  { id: "purpose",      label: "Purpose & Meaning" },
  { id: "equanimity",   label: "Equanimity" },
];

var activeTopic = null;
var shownIndex  = null;

function shuffle(arr) {
  var a = arr.slice();
  for (var i = a.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var t = a[i]; a[i] = a[j]; a[j] = t;
  }
  return a;
}

function renderTopics() {
  var el = document.getElementById('gita-topics');
  if (!el) return;
  el.innerHTML = TOPICS.map(function(t) {
    var active = activeTopic === t.id ? ' gita-chip--active' : '';
    return '<button class="gita-chip' + active + '" onclick="gitaSelect(\'' + t.id + '\')">' + t.label + '</button>';
  }).join('');
}

function renderVerse(verse) {
  var el = document.getElementById('gita-verse-area');
  if (!el) return;
  el.innerHTML =
    '<div class="gita-card">' +
      '<div class="gita-ref">Bhagavad Gita · ' + verse.ref + '</div>' +
      '<div class="gita-sanskrit">' + verse.sanskrit.replace(/\n/g, '<br>') + '</div>' +
      '<div class="gita-translit">' + verse.transliteration.replace(/\n/g, '<br>') + '</div>' +
      '<div class="gita-translation">' + verse.translation + '</div>' +
      '<button class="gita-another-btn" onclick="gitaAnother()">Another verse</button>' +
    '</div>';
}

function renderEmpty() {
  var el = document.getElementById('gita-verse-area');
  if (el) el.innerHTML = '';
}

window.gitaSelect = function(topicId) {
  activeTopic = topicId;
  renderTopics();
  var pool = VERSES.filter(function(v) { return v.topics.indexOf(topicId) !== -1; });
  if (!pool.length) { renderEmpty(); return; }
  var shuffled = shuffle(pool);
  shownIndex = 0;
  renderVerse(shuffled[shownIndex]);
  window._gitaPool = shuffled;
};

window.gitaAnother = function() {
  if (!window._gitaPool || !window._gitaPool.length) return;
  shownIndex = (shownIndex + 1) % window._gitaPool.length;
  renderVerse(window._gitaPool[shownIndex]);
};

renderTopics();

})();
</script>

<style>
.gita-intro { font-size: 0.9rem; color: var(--gray); margin-bottom: 1.25rem; }

.gita-topics {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 2rem;
}

.gita-chip {
  font-family: var(--bodyFont);
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--darkgray);
  background: var(--lightgray);
  border: 1px solid transparent;
  border-radius: 20px;
  padding: 0.35rem 0.9rem;
  cursor: pointer;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
  white-space: nowrap;
}
.gita-chip:hover {
  background: var(--secondary);
  color: #fff;
}
.gita-chip--active {
  background: var(--secondary);
  color: #fff;
  border-color: var(--secondary);
}

.gita-card {
  border: 1px solid var(--lightgray);
  border-left: 3px solid var(--secondary);
  border-radius: 6px;
  padding: 1.75rem 2rem;
  background: var(--light);
  animation: gita-fadein 0.25s ease;
}

@keyframes gita-fadein {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}

.gita-ref {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--secondary);
  margin-bottom: 1.1rem;
}

.gita-sanskrit {
  font-family: 'Noto Sans Devanagari', 'Mangal', serif;
  font-size: 1.05rem;
  line-height: 1.85;
  color: var(--dark);
  margin-bottom: 1rem;
}

.gita-translit {
  font-size: 0.85rem;
  line-height: 1.75;
  color: var(--gray);
  font-style: italic;
  margin-bottom: 1.1rem;
  border-left: 2px solid var(--lightgray);
  padding-left: 0.85rem;
}

.gita-translation {
  font-size: 0.95rem;
  line-height: 1.7;
  color: var(--darkgray);
  margin-bottom: 1.5rem;
}

.gita-another-btn {
  font-family: var(--bodyFont);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--secondary);
  background: transparent;
  border: 1px solid var(--secondary);
  border-radius: 4px;
  padding: 0.35rem 0.85rem;
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
}
.gita-another-btn:hover {
  background: var(--secondary);
  color: #fff;
}

@media (max-width: 640px) {
  .gita-card { padding: 1.25rem 1rem; }
  .gita-sanskrit { font-size: 0.95rem; }
}
</style>
