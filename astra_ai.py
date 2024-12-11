# astra_ai.py
import os
import json
import ollama
from rich.console import Console
from typing import List, Dict, Optional, Tuple, Any
from PyPDF2 import PdfReader
from docx import Document

console = Console()


class AstraAI:
    """ASTRA AI Study Assistant Class"""

    def __init__(self) -> None:
        """Initialize all class attributes"""
        # Model configuration
        self.model: str = "llama3.2"  # Specify exact model version

        # Conversation state
        self.conversation_active: bool = True
        self.chat_history: List[Dict[str, str]] = []

        # Document handling
        self.context: str = ""
        self.document_name: Optional[str] = None

        # Console for logging
        self.console: Console = Console()

        # Quiz-related attributes
        self.quiz_active: bool = False
        self.current_quiz: List[Dict[str, Any]] = []
        self.quiz_progress: int = 0
        self.quiz_score: int = 0
        self.total_questions: int = 0

        # Error handling
        self.last_error: Optional[str] = None

    def load_document(self, file_path: str) -> str:
        """
        Load and process document content based on file type

        Args:
            file_path (str): Path to the document file

        Returns:
            str: Extracted text content from the document
        """
        try:
            self.document_name = os.path.basename(file_path)
            file_extension = os.path.splitext(file_path)[1].lower()

            content = ""
            if file_extension == '.txt':
                content = self._read_txt(file_path)
            elif file_extension == '.pdf':
                content = self._read_pdf(file_path)
            elif file_extension == '.docx':
                content = self._read_docx(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")

            # Basic content validation
            if not content.strip():
                raise ValueError("Document appears to be empty")

            return content

        except Exception as e:
            self.last_error = str(e)
            self.console.print(f"[red]Error loading document: {str(e)}[/red]")
            return ""

    def _read_txt(self, file_path: str) -> str:
        """Read text file content with proper encoding handling"""
        encodings = ['utf-8', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
        raise ValueError("Unable to decode file with supported encodings")

    def _read_pdf(self, file_path: str) -> str:
        """Read PDF file content with enhanced error handling"""
        try:
            text = []
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                for page in pdf_reader.pages:
                    content = page.extract_text()
                    if content:
                        text.append(content)
            return "\n".join(text)
        except Exception as e:
            raise ValueError(f"PDF reading error: {str(e)}")

    def _read_docx(self, file_path: str) -> str:
        """Read DOCX file content with paragraph spacing"""
        try:
            doc = Document(file_path)
            return "\n\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
        except Exception as e:
            raise ValueError(f"DOCX reading error: {str(e)}")

    def ask_question(self, question: str) -> str:
        """
        Process user question and generate response

        Args:
            question (str): User's question

        Returns:
            str: AI-generated response
        """
        try:
            if not question.strip():
                return "Please ask a valid question."

            if self._should_end_conversation(question):
                self.conversation_active = False
                return "Goodbye! Feel free to start a new conversation when you need help!"

            messages = self._prepare_messages(question)
            response = self._generate_response(messages)
            self._update_chat_history(question, response)

            return response

        except Exception as e:
            self.last_error = str(e)
            error_msg = "I apologize, but I encountered an error processing your question. Please try again."
            self.console.print(f"[red]Error: {str(e)}[/red]")
            return error_msg

    def _should_end_conversation(self, question: str) -> bool:
        """Check if the conversation should end based on user input"""
        end_phrases = {'goodbye', 'bye', 'exit', 'quit', 'end'}
        return any(phrase in question.lower().split() for phrase in end_phrases)

    def _prepare_messages(self, question: str) -> List[Dict[str, str]]:
        """Prepare messages for the chat model with improved context handling"""
        # Limit context size based on model's context window
        max_context = 1500  # Adjusted for TinyLlama's context window
        context_preview = self.context[:max_context] if self.context else ""

        system_message = {
            "role": "system",
            "content": """You are ASTRA AI, a helpful study assistant. Keep responses concise and relevant.
            If a document is loaded, use its content to provide accurate answers. Maintain a friendly and
            educational tone while being precise and informative."""
        }

        messages = [system_message]

        # Add recent chat history for context
        messages.extend(self.chat_history[-3:])  # Last 3 exchanges for context

        if context_preview and self.document_name:
            messages.append({
                "role": "system",
                "content": f"Using content from document: {self.document_name}\n\n{context_preview}"
            })

        messages.append({
            "role": "user",
            "content": question
        })

        return messages

    def _generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using Ollama with enhanced error handling"""
        try:
            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": 0.7,
                    "num_ctx": 2048,
                    "top_p": 0.9,
                    "top_k": 40,
                }
            )
            return response['message']['content']
        except Exception as e:
            raise RuntimeError(f"Error generating response: {str(e)}")

    def _update_chat_history(self, question: str, response: str) -> None:
        """Update chat history with message validation"""
        if question.strip() and response.strip():
            self.chat_history.append({"role": "user", "content": question})
            self.chat_history.append({"role": "assistant", "content": response})

    def reset_conversation(self) -> None:
        """Reset all conversation and quiz state"""
        self.chat_history = []
        self.conversation_active = True
        self.context = ""
        self.document_name = None
        self.end_quiz()
        self.last_error = None

    def end_quiz(self) -> None:
        """End the current quiz and reset quiz-related attributes"""
        self.quiz_active = False
        self.current_quiz = []
        self.quiz_progress = 0
        self.quiz_score = 0
        self.total_questions = 0

    def generate_quiz(self, num_questions: int = 5) -> bool:
        """
        Generate a quiz with improved formatting and error handling

        Args:
            num_questions (int): Number of questions to generate

        Returns:
            bool: True if quiz generation successful, False otherwise
        """
        if not self.context:
            self.last_error = "No document loaded for quiz generation"
            return False

        try:
            # Create a more structured prompt for reliable formatting
            prompt = f"""Generate {num_questions} multiple choice questions based on this text. 
            Make questions that test understanding of key concepts.

            Text for quiz: {self.context[:2000]}...

            Format each question exactly like this example:

            1. Question text goes here?
            A) First option
            B) Second option
            C) Third option
            D) Fourth option
            CORRECT: B
            EXPLANATION: Explanation of why B is correct goes here.

            Generate {num_questions} questions in exactly this format, numbered from 1 to {num_questions}.
            """

            # Generate quiz content
            response = ollama.chat(
                model=self.model,
                messages=[{
                    "role": "system",
                    "content": "You are a quiz generator. Generate clear, focused questions with exactly four options (A, B, C, D). Provide the correct answer and explanation for each question."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                options={
                    "temperature": 0.7,
                    "num_ctx": 2048,
                }
            )

            # Parse the response into structured quiz format
            quiz_questions = self._parse_quiz_response(response['message']['content'])

            if not quiz_questions:
                self.last_error = "Failed to generate valid quiz questions"
                return False

            self.current_quiz = quiz_questions
            self.quiz_active = True
            self.quiz_progress = 0
            self.quiz_score = 0
            self.total_questions = len(quiz_questions)
            return True

        except Exception as e:
            self.last_error = f"Quiz generation error: {str(e)}"
            self.console.print(f"[red]Error generating quiz: {str(e)}[/red]")
            return False

    def _parse_quiz_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse quiz response into structured format

        Args:
            response_text (str): Raw quiz response from LLM

        Returns:
            List[Dict[str, Any]]: Structured quiz questions
        """
        try:
            questions = []
            current_question = None

            # Split response into lines and process
            lines = response_text.strip().split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # New question starts with a number
                if line[0].isdigit() and '. ' in line:
                    if current_question:
                        questions.append(current_question)
                    current_question = {
                        'question': line.split('. ', 1)[1],
                        'options': {},
                        'correct': None,
                        'explanation': None
                    }

                # Option line
                elif line[0] in 'ABCD' and ') ' in line:
                    option, text = line.split(') ', 1)
                    if current_question:
                        current_question['options'][option] = text.strip()

                # Correct answer line
                elif line.startswith('CORRECT:'):
                    if current_question:
                        current_question['correct'] = line.split(':', 1)[1].strip()

                # Explanation line
                elif line.startswith('EXPLANATION:'):
                    if current_question:
                        current_question['explanation'] = line.split(':', 1)[1].strip()
                        questions.append(current_question)
                        current_question = None

            # Add last question if exists
            if current_question and current_question['explanation']:
                questions.append(current_question)

            # Validate questions
            valid_questions = []
            for q in questions:
                if self._validate_question(q):
                    valid_questions.append(q)

            return valid_questions

        except Exception as e:
            self.console.print(f"[red]Error parsing quiz response: {str(e)}[/red]")
            return []

    def _validate_question(self, question: Dict) -> bool:
        """
        Validate a single quiz question

        Args:
            question (Dict): Question dictionary to validate

        Returns:
            bool: True if question is valid, False otherwise
        """
        try:
            # Check required fields
            required_fields = ['question', 'options', 'correct', 'explanation']
            if not all(field in question for field in required_fields):
                return False

            # Validate options
            if not all(opt in question['options'] for opt in ['A', 'B', 'C', 'D']):
                return False

            # Validate correct answer
            if question['correct'] not in ['A', 'B', 'C', 'D']:
                return False

            # Validate content
            if not question['question'] or not question['explanation']:
                return False

            return True

        except Exception:
            return False

    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """Get current quiz question with formatted output"""
        if not self.quiz_active or self.quiz_progress >= len(self.current_quiz):
            return None

        question = self.current_quiz[self.quiz_progress]
        return {
            'question': question['question'],
            'options': question['options'],
            'correct': question['correct'],
            'explanation': question['explanation']
        }

    def submit_answer(self, answer: str) -> Tuple[bool, str]:
        """Submit and validate quiz answer with improved feedback"""
        if not self.quiz_active:
            return False, "No quiz is active"

        current_question = self.get_current_question()
        if not current_question:
            return False, "No current question"

        answer = answer.upper()
        if answer not in ['A', 'B', 'C', 'D']:
            return False, "Invalid answer option"

        is_correct = answer == current_question['correct']
        if is_correct:
            self.quiz_score += 1

        self.quiz_progress += 1

        if self.quiz_progress >= self.total_questions:
            self.quiz_active = False

        feedback = current_question['explanation']
        if is_correct:
            feedback = f"✅ Correct! {feedback}"
        else:
            feedback = f"❌ Incorrect. The correct answer was {current_question['correct']}. {feedback}"

        return is_correct, feedback

    def get_quiz_status(self) -> Dict[str, Any]:
        """Get detailed quiz status with additional metrics"""
        return {
            'active': self.quiz_active,
            'progress': self.quiz_progress,
            'total_questions': self.total_questions,
            'score': self.quiz_score,
            'percentage': round((self.quiz_score / self.total_questions * 100) if self.total_questions > 0 else 0, 1),
            'remaining': self.total_questions - self.quiz_progress if self.quiz_active else 0,
            'current_streak': self._calculate_current_streak()
        }

    def _calculate_current_streak(self) -> int:
        """Calculate the current streak of correct answers"""
        streak = 0
        for i in range(self.quiz_progress - 1, -1, -1):
            if hasattr(self, '_answer_history') and len(self._answer_history) > i:
                if self._answer_history[i]:
                    streak += 1
                else:
                    break
            else:
                break
        return streak