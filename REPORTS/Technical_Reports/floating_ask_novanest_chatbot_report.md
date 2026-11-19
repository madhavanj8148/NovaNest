# Floating, Blinking AI Chatbot Widget (Ask NovaNest) — Implementation Report

**Project:** NovaNest — End-To-End Business Analytics System  
**Feature:** Global Floating & Pulsing AI Assistant Widget  
**Status:** Verification Complete & Fully Operational on Localhost  
**Date:** 2026-10-12  

---

## Executive Summary

The **Ask NovaNest AI** conversational intelligence system has been transformed into a **permanently accessible, floating, blinking/pulsing AI chatbot widget**.

Positioned fixed in the bottom-right corner of the platform, the floating button features a modern AI assistant beacon with a subtle breathing glow and pulsing indicator. When clicked, it smoothly expands into an interactive glassmorphic chat window without navigating away from the current page.

The widget is mounted globally in the shared root layout (`App.tsx`), ensuring that users can converse with NovaNest AI while exploring the **Homepage**, **Customer Intelligence**, **Restaurant Intelligence**, **Operations Intelligence**, **Financial Intelligence**, **Decision Intelligence**, **Decision Simulator**, **Command Center**, or the dedicated **Ask NovaNest AI View**, with conversation context preserved across all tab transitions.

---

## 1. Components Created & Modified

### New Components
1. **[frontend/src/components/FloatingChatbot.tsx](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/frontend/src/components/FloatingChatbot.tsx)**
   - Houses the floating trigger button and floating chat dialog.
   - Includes embedded `MiniCodeBlock` with one-click clipboard copy (`navigator.clipboard.writeText`).
   - Includes `MiniFormattedContent` supporting Markdown headers, bolding, bullet/numbered lists, inline code, and responsive data tables.
   - Manages state for `isOpen`, `messages`, `input`, `loading`, `sessionId`, and `hasUnread`.
   - Displays real verified metrics badges, provenance tags, and follow-up chips.

### Modified Files
2. **[frontend/src/App.tsx](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/frontend/src/App.tsx)**
   - Imported and mounted `<FloatingChatbot />` at the root layout level, outside of viewport content tabs.
   - Guarantees single-instance global persistence across all views without duplicate buttons.
3. **[frontend/src/index.css](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/frontend/src/index.css)**
   - Added keyframe `@keyframes botGlowPulse`: smooth 2.8s breathing pulse transitioning sapphire and cyan glow shadows.
   - Added keyframe `@keyframes beaconBlink`: subtle 2.0s opacity and scale indicator.
   - Added `@media (prefers-reduced-motion: reduce)` accessibility rule to disable animations when reduced motion is preferred by the operating system.
4. **[tests/test_floating_chatbot_verification.py](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/tests/test_floating_chatbot_verification.py)**
   - Automated verification suite covering component structure, CSS animations, suggested questions, real AI backend requests, multi-turn follow-ups, and session reset.

---

## 2. Floating Widget Design & Behavior

### A. Floating Trigger Button (Bottom-Right)
- **Positioning:** `fixed bottom-6 right-5 sm:right-6 z-50` (remains visible during scrolling without covering primary charts or navigation).
- **Appearance:**
  - Pill-shaped gradient badge: `bg-gradient-to-r from-obsidian-900 via-obsidian-850 to-slate-900` with sapphire border (`border-sapphire-500/70`).
  - Pulsing beacon dot: Dual-ring cyan indicator with subtle ping and breathing blink.
  - Assistant Icon: Glowing `Sparkles` icon that rotates on hover.
  - Label: `"Ask NovaNest"` with subtitle `"AI Assistant"`.
  - Unread Badge: Displays a red counter if a response completes while minimized.
  - Animation: Uses `animate-bot-glow` for a non-distracting breathing glow; stops attention-seeking animation when the window is open.

### B. Chatbot Window
- **Positioning:** `fixed bottom-5 right-4 sm:bottom-6 sm:right-6 z-50 w-[calc(100vw-2rem)] sm:w-[420px] md:w-[460px] h-[580px]`.
- **Styling:** Premium dark glassmorphism (`bg-obsidian-900/95 backdrop-blur-2xl border border-slate-700/70 shadow-2xl`).
- **Header:**
  - Gradient accent bar (`from-sapphire-500 via-cyan-400 to-indigo-500`).
  - NovaNest AI icon + Title: `"Ask NovaNest AI"` + Subtitle: `"Your Intelligent Business Assistant"`.
  - Live status indicator: `"Online"` with pulsing green dot.
  - Action controls:
    - **New Chat / Reset Conversation (`RotateCcw`):** Resets conversation context both locally and on the server via `POST /api/ai/reset`.
    - **Minimize (`Minus`):** Minimizes the chat window while preserving messages.
    - **Close (`X`):** Closes the window.
- **Welcome & Starter Chips:**
  - Initial greeting: *"Hi! I'm NovaNest AI. Ask me about your business data, analytics, programming, or any other topic. How can I help you today?"*
  - Clickable suggested chips:
    - *"Analyze my business performance."*
    - *"What is our total revenue?"*
    - *"Explain customer churn."*
    - *"How can I improve restaurant performance?"*
    - *"Explain a technical concept."*
    - *"Help me write Python or SQL code."*
- **Chat Interface:**
  - User messages in sapphire bubbles on the right.
  - Assistant messages in obsidian glass bubbles on the left with markdown, tables, and syntax code blocks.
  - Auto-scrolling to bottom on new messages.
  - Auto-resizing input textarea with `Enter` to send and `Shift + Enter` for new line.
  - Non-blocking loading indicator with animated spinner and thinking status.

---

## 3. Real AI Backend Integration

The widget connects directly to the existing production backend endpoints:

- **Endpoint:** `POST /api/ai/ask`
- **Payload:** `{ "question": string, "session_id": string }`
- **Intelligence Flow:**
  - Queries are processed through the `Universal Query Classifier` ([python/ai/analyst/universal_router.py](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/python/ai/analyst/universal_router.py)).
  - General inquiries, programming questions, and mathematical calculations are answered via the universal reasoning engine without querying the business database.
  - Business inquiries retrieve verified metrics from NovaNest's orders, customers, and restaurants datasets (e.g. ₹4.90 Cr GMV, 4.16% cancellation rate, 5,000 customers).
  - Multi-turn follow-ups are resolved using isolated session history ([python/ai/analyst/conversation_manager.py](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/python/ai/analyst/conversation_manager.py)).
  - When `GEMINI_API_KEY` is present, answers are synthesized using Google Gemini (`gemini-2.5-flash`). When absent, the system operates deterministically using verified telemetry and exact formulas.

---

## 4. Pages Where the Chatbot is Available

Because `<FloatingChatbot />` is mounted at the root level of `App.tsx`, it is permanently accessible across all application views:

1. **Homepage / Executive Overview:** `activeTab === 'overview'` (displays over hero banner and KPI cards).
2. **Customer Intelligence:** `activeTab === 'customer'` (accessible alongside RFM cohorts and CLV tiers).
3. **Restaurant Intelligence:** `activeTab === 'restaurant'` (accessible alongside merchant health matrices).
4. **Operations Intelligence:** `activeTab === 'operations'` (accessible alongside rider allocation and demand heatmaps).
5. **Financial Intelligence:** `activeTab === 'financial'` (accessible alongside unit economics and margin leakage).
6. **Decision Intelligence:** `activeTab === 'decision'` (accessible alongside Next-Best-Actions).
7. **Decision Simulator:** `activeTab === 'simulator'` (accessible alongside Monte Carlo sliders).
8. **Command Center:** `activeTab === 'command_center'` (accessible alongside system vitality alerts).
9. **Ask NovaNest AI (Full View):** `activeTab === 'ai'`.

Navigation between these views never resets or disrupts an active conversation.

---

## 5. Verification & Tests Executed

### Test Suite 1: Floating Chatbot Suite (`tests/test_floating_chatbot_verification.py`)
```
Ran 9 tests in 1.143s — OK (100% Passed)
```
- `test_01_component_and_styles_exist`: Validated UI elements, welcome text, suggestions, and CSS classes. **[PASS]**
- `test_02_global_mount_in_app`: Verified `<FloatingChatbot />` is rendered at root level in `App.tsx`. **[PASS]**
- `test_03_css_animations_and_accessibility`: Verified `@keyframes botGlowPulse`, `@keyframes beaconBlink`, and `prefers-reduced-motion`. **[PASS]**
- `test_04_floating_chat_business_performance`: Verified suggested question "Analyze my business performance." **[PASS]**
- `test_05_floating_chat_total_revenue`: Verified suggested question "What is our total revenue?" (returns verified ₹4.90 Cr). **[PASS]**
- `test_06_floating_chat_customer_churn`: Verified suggested question "Explain customer churn." **[PASS]**
- `test_07_floating_chat_python_code`: Verified suggested question "Help me write Python code to calculate average of a list." (returns code block). **[PASS]**
- `test_08_floating_chat_multi_turn_follow_up`: Verified multi-turn session (Turn 1: Cancellation rate -> Turn 2: Which restaurant has highest rate -> Turn 3: How to improve it -> Reset session). **[PASS]**
- `test_09_floating_chat_general_knowledge`: Verified arbitrary general knowledge question ("How does GPS work?") without business KPI cards. **[PASS]**

### Test Suite 2: Universal AI Assistant Suite (`tests/test_universal_ai_suite.py`)
```
Ran 15 tests in 1.942s — OK (100% Passed)
```

### Test Suite 3: Full Platform Verification Suite (`tests/test_platform_full_suite.py`)
```
ALL VERIFICATION CHECKS PASSED: PLATFORM HEALTHY & READY (100% Passed)
- REST Endpoints: 12 of 12 Passed (HTTP 200)
- Vite Dev Server: HTTP 200 at http://localhost:5173
- Production Build: Clean TypeScript compilation (0 errors)
- Streamlit Hub: HTTP 200 at http://localhost:8501
- Cleaned & Engineered Datasets: 20 tables verified intact
```

---

## 6. Remaining Issues / Notes

- **Zero Breaking Changes:** No database schemas, existing APIs, or analytics algorithms were altered.
- **Localhost Only:** All files and services are running locally on Windows without remote Git pushes or external dependencies.
