import jakarta.servlet.ServletException;
import jakarta.servlet.http.*;
import jakarta.servlet.annotation.WebServlet;
import java.io.*;
import java.lang.reflect.Array;
import java.sql.*;
import com.google.gson.Gson;
import java.lang.*;
import java.util.Arrays;

@WebServlet("/submitQuiz")
public class submitQuizServlet extends HttpServlet {

    // Handle POST request to submit quiz data
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        // Read the JSON data from the request
        BufferedReader reader = new BufferedReader(new InputStreamReader(request.getInputStream()));
        StringBuilder jsonData = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            jsonData.append(line);
        }

        try {
            // Use Gson to parse the JSON data into a Java object
            Gson gson = new Gson();
            QuizData quizData = gson.fromJson(jsonData.toString(), QuizData.class);

            String rollNo = quizData.getRollNo();
            int[] selectedAnswers = quizData.getAnswers(); // Array of selected answers
            System.out.println("Received Roll No: " + rollNo);
            System.out.println("Received Answers: " + Arrays.toString(selectedAnswers));

            // Database connection setup
            Class.forName("com.mysql.cj.jdbc.Driver");
            Connection conn = DriverManager.getConnection(
                    "jdbc:mysql://localhost:3306/smart_classroom", "root", "tiger"
            );

            // Assume correct answers are stored as an array, e.g., correct answers for each question
            int[] correctAnswers = {1, 2, 3, 4, 1}; // Example correct answers (you should get this dynamically or from DB)

            String sql = "INSERT INTO quiz_results (roll_no, question_no, selected_option, correct_option, is_correct) VALUES (?, ?, ?, ?, ?)";
            PreparedStatement stmt = conn.prepareStatement(sql);

            // Ensure the answers length matches
            if (selectedAnswers.length != correctAnswers.length) {
                response.setStatus(400);
                response.getWriter().write("Error: The number of selected answers does not match the number of questions.");
                return;
            }

            // Insert each answer and check if it's correct
            for (int i = 0; i < selectedAnswers.length; i++) {
                int qNo = i + 1;
                int selected = selectedAnswers[i];
                int correct = correctAnswers[i];
                boolean isCorrect = (selected == correct);

                stmt.setString(1, rollNo);
                stmt.setInt(2, qNo);
                stmt.setInt(3, selected);
                stmt.setInt(4, correct);
                stmt.setBoolean(5, isCorrect);
                System.out.println("Inserting -> RollNo: " + rollNo + ", Q: " + qNo + ", Selected: " + selected + ", Correct: " + correct + ", Correct? " + isCorrect);
                stmt.executeUpdate();
            }

            conn.close();
            response.setStatus(200);
            response.getWriter().write("Quiz submitted successfully!");

        } catch (Exception e) {
            e.printStackTrace();
            response.setStatus(500);
            response.getWriter().write("Error: " + e.getMessage());
        }
    }

    // New servlet to retrieve quiz results based on roll number
    @WebServlet("/getQuizResults")
    public static class GetQuizResultsServlet extends HttpServlet {

        protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
            String rollNo = request.getParameter("rollNo");  // Get roll number from request parameters

            if (rollNo == null || rollNo.isEmpty()) {
                response.setStatus(400);
                response.getWriter().write("Roll number is required");
                return;
            }

            try {
                // Database connection setup
                Class.forName("com.mysql.cj.jdbc.Driver");
                Connection conn = DriverManager.getConnection(
                        "jdbc:mysql://localhost:3306/smart_classroom", "root", "tiger"
                );

                // Query to fetch quiz results for the given roll number
                String sql = "SELECT question_no, selected_option, correct_option, is_correct, submission_time FROM quiz_results WHERE roll_no = ?";
                PreparedStatement stmt = conn.prepareStatement(sql);
                stmt.setString(1, rollNo);

                ResultSet rs = stmt.executeQuery();
                StringBuilder resultBuilder = new StringBuilder();
                resultBuilder.append("Quiz Results for Roll Number: ").append(rollNo).append("\n");

                while (rs.next()) {
                    int questionNo = rs.getInt("question_no");
                    int selectedOption = rs.getInt("selected_option");
                    int correctOption = rs.getInt("correct_option");
                    boolean isCorrect = rs.getBoolean("is_correct");
                    Timestamp submissionTime = rs.getTimestamp("submission_time");

                    resultBuilder.append("Question: ").append(questionNo)
                            .append(" | Selected: ").append(selectedOption)
                            .append(" | Correct: ").append(correctOption)
                            .append(" | Correct? ").append(isCorrect)
                            .append(" | Submitted on: ").append(submissionTime).append("\n");
                }

                conn.close();
                response.setStatus(200);
                response.getWriter().write(resultBuilder.toString());

            } catch (Exception e) {
                e.printStackTrace();
                response.setStatus(500);
                response.getWriter().write("Error: " + e.getMessage());
            }
        }
    }

    // Inner class to map the quiz data from the client
    public static class QuizData {
        private String rollNo;
        private int[] answers; // Array to hold answers selected by the student

        public String getRollNo() {
            return rollNo;
        }

        public void setRollNo(String rollNo) {
            this.rollNo = rollNo;
        }

        public int[] getAnswers() {
            return answers;
        }

        public void setAnswers(int[] answers) {
            this.answers = answers;
        }
    }
}
