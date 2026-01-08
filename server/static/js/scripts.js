// הודעות Flash מסתירות אחרי 5 שניות
window.addEventListener("DOMContentLoaded", () => {
  const flashMessages = document.getElementById("flash-messages");
  if (flashMessages) {
    setTimeout(() => {
      flashMessages.style.display = "none";
    }, 5000);
  }
});

// כפתורי הרצת הגרלה
function confirmLottery(classId) {
  const confirmed = confirm("האם אתה בטוח שאתה רוצה להריץ הגרלה לכיתה זו?");
  if (confirmed) {
    window.location.href = `/admin/run_lottery/${classId}`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const lotteryButtons = document.querySelectorAll(".run-lottery-btn");
  lotteryButtons.forEach(btn => {
    btn.addEventListener("click", (e) => {
      const classId = e.target.dataset.classId;
      confirmLottery(classId);
    });
  });

  // כפתורי "לא יכול השבוע" בכיתה
  const cannotButtons = document.querySelectorAll(".cannot-btn");
  cannotButtons.forEach(btn => {
    btn.addEventListener("click", async (e) => {
      const studentId = e.target.dataset.student;
      const week = e.target.dataset.week;
      if (confirm(`לסמן את התלמיד כ"לא יכול" בשבוע ${week}?`)) {
        try {
          const res = await fetch(`/admin/student/unavailable`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ student_id: studentId, week: week })
          });
          if (res.ok) {
            alert("סטטוס עודכן בהצלחה!");
            location.reload();
          } else {
            alert("שגיאה בעדכון הסטטוס");
          }
        } catch (err) {
          console.error(err);
          alert("שגיאה ברשת");
        }
      }
    });
  });
});
