import streamlit as st
from google import genai
from pydantic import BaseModel

# Βάζεις το κλειδί σου εδώ απευθείας ανάμεσα στα εισαγωγικά:
API_KEY = "AQ.Ab8RN6IUKzgcH01LpTcWRshkw3iAQVUmiOAf6R5RnlohSCgLlQ"


# 1. Ορίζουμε τη δομή για τις ερωτήσεις του Quiz
class Question(BaseModel):
    question_text: str
    options: list[str]
    correct_answer: str
    explanation: str


class Quiz(BaseModel):
    questions: list[Question]


st.set_page_config(page_title="AI Study Buddy", page_icon="🧠")
st.title("🧠 AI Study Buddy & Quiz Generator")
st.write("Επικόλλησε τις σημειώσεις σου και άσε το AI να φτιάξει ένα διαδραστικό τεστ για σένα!")

# --- ΝΕΟ: Επιλογή Δυσκολίας ---
difficulty = st.selectbox(
    "Επίλεξε δυσκολία quiz:",
    ["Εύκολο (Βασικές έννοιες)", "Μέτριο (Κατανόηση)", "Δύσκολο (Προχωρημένο / Πονηρό)"]
)

notes = st.text_area("Επικόλλησε εδώ το κείμενο ή τις σημειώσεις του μαθήματος:", height=200)
num_questions = st.slider("Πόσες ερωτήσεις θέλεις;", min_value=3, max_value=10, value=5)

if st.button("✨ Δημιουργία Quiz"):
    if not notes.strip():
        st.warning("Γράψε ή επικόλλησε πρώτα μερικές σημειώσεις!")
    else:
        with st.spinner("Το AI διαβάζει τις σημειώσεις σου και φτιάχνει ερωτήσεις..."):
            try:
                client = genai.Client(api_key=API_KEY)

                # Προσθέτουμε τη δυσκολία στο prompt προς το Gemini
                prompt = f"""
                Διάβασε προσεκτικά τις παρακάτω σημειώσεις και φτιάξε {num_questions} ερωτήσεις πολλαπλής επιλογής (με 4 επιλογές η καθεμία) στα Ελληνικά.
                Επίπεδο δυσκολίας: {difficulty}.
                Βεβαιώσου ότι η σωστή απάντηση (correct_answer) είναι ακριβώς ίδια με μία από τις 4 επιλογές (options).

                Σημειώσεις:
                {notes}
                """

                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": Quiz,
                    },
                )

                st.session_state.quiz_data = response.parsed
                st.success("Το Quiz είναι έτοιμο! Απάντησε στις ερωτήσεις παρακάτω:")
            except Exception as e:
                st.error(f"Κάτι πήγε στραβά: {e}")

if "quiz_data" in st.session_state:
    quiz = st.session_state.quiz_data
    st.divider()

    with st.form("quiz_form"):
        user_answers = {}
        for i, q in enumerate(quiz.questions):
            st.subheader(f"Ερώτηση {i + 1}: {q.question_text}")
            user_answers[i] = st.radio(
                "Διάλεξε απάντηση:",
                q.options,
                key=f"q_{i}",
                index=None
            )
            st.write("")

        submitted = st.form_submit_button("✅ Έλεγχος Απαντήσεων")

        if submitted:
            score = 0
            for i, q in enumerate(quiz.questions):
                if user_answers[i] == q.correct_answer:
                    score += 1
                    st.success(f"**Ερώτηση {i + 1}: Σωστό!** ({q.correct_answer})")
                else:
                    st.error(
                        f"**Ερώτηση {i + 1}: Λάθος.** Διάλεξες: *{user_answers[i]}* | Σωστό: **{q.correct_answer}**")
                st.info(f"💡 Εξήγηση: {q.explanation}")

            st.metric(label="Τελικό Σκορ", value=f"{score} / {len(quiz.questions)}")