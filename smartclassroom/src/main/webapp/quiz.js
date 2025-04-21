console.log("quiz.js loaded");

const questions = [
    {
      question: "What is the primary function of web browser ?",
      options: ["to create documents", "to browse the internet", "to plsy games", "to edit videos"],
      correct: 1
    },
    {
      question: "Which software is used for creating spreadsheets?",
      options: ["Microsoft Word", "Microsoft PowerPoint", "Microsoft Excel", "Adobe Photoshop"],
      correct: 2
    },
    {
      question: "HTML stands for?",
      options: ["Hyperlinks Text Markup", "Hyper Tool Markup Language", "Hyper Text Markup Language", "None"],
      correct: 2
    }
  ];

  let currentQuestion = 0;
  let rollNumber = '';
  let selectedAnswers = [];

  function startQuiz() {
    rollNumber = document.getElementById("rollNo").value.trim();
    if (!rollNumber) {
      alert("Please enter your roll number!");
      return;
    }

    document.getElementById("loginSection").style.display = "none";
    document.getElementById("quizSection").style.display = "block";
    loadQuestion();
  };

  function loadQuestion() {
    const q = questions[currentQuestion];
    document.getElementById("questionText").innerText = q.question;
    const container = document.getElementById("optionsContainer");
    container.innerHTML = "";

    q.options.forEach((option, index) => {
      const btn = document.createElement("div");
      btn.className = "option";
      btn.innerText = option;
      btn.onclick = () => {
        selectedAnswers[currentQuestion] = index;

          // 🔄 Remove 'selected' class from all options
        const allOptions = document.querySelectorAll(".option");
    allOptions.forEach(opt => opt.classList.remove("selected"));

    // ✅ Add 'selected' to the clicked one
    btn.classList.add("selected");
        document.getElementById("nextBtn").style.display = "inline-block";
      };
      container.appendChild(btn);
    });

    document.getElementById("nextBtn").style.display = "none";
  };

  function nextQuestion() {
    currentQuestion++;
    if (currentQuestion < questions.length) {
      loadQuestion();
    } else {
      showResults();
    }
  }

  function showResults() {
    document.getElementById("quizSection").style.display = "none";
    document.getElementById("resultSection").style.display = "block";

    let summaryHTML = `<h3>Result for Roll No: ${rollNumber}</h3><ul>`;
    let correct = 0;

    questions.forEach((q, index) => {
      const userAnswer = selectedAnswers[index];
      const isCorrect = userAnswer === q.correct;
      summaryHTML += `<li>Q${index + 1}: ${q.question}<br>
          Your Answer: <b>${q.options[userAnswer] || "No Answer"}</b> -
          <span style="color:${isCorrect ? 'green' : 'red'};">${isCorrect ? "Correct" : "Wrong"}</span></li><br>`;
      if (isCorrect) correct++;
    });

    summaryHTML += `</ul><h4>Total Correct: ${correct} / ${questions.length}</h4>`;
    document.getElementById("summary").innerHTML = summaryHTML;

    // OPTIONAL: send data to backend (Java + MySQL)
    sendResultsToBackend(rollNumber, selectedAnswers);
  }

   function sendResultsToBackend(rollNo, selectedAnswers) {
     const data = {
       rollNo: rollNo,
       answers: selectedAnswers  // This should be like [1, 2, 3, 4, 1]
     };

     console.log("Sending to server:", data);  // Debug log

     fetch("http://localhost:8080/smartclassroom/submitQuiz", {
       method: "POST",
       headers: {
         "Content-Type": "application/json"
       },
       body: JSON.stringify(data)
     })
     .then(response => response.text())
     .then(message => {
       console.log("Server Response:", message);
       alert("Quiz response saved successfully!");
     })
     .catch(error => {
       console.error("Error sending data:", error);
       alert("Failed to submit quiz results.");
     });
   }

