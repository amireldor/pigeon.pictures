import { useEffect, useState } from "react";

const ProgressBar = () => {
  const [progress, setProgress] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState("");
  const [remaining, setRemaining] = useState(0);

  useEffect(() => {
    const updateProgress = () => {
      const current = new Date();
      const nextPigeons = new Date(window.nextPigeonsISODate);
      const periodStart = new Date(nextPigeons.getTime() - window.pigeonPeriod);

      const elapsed = current.getTime() - periodStart.getTime();
      const total = nextPigeons.getTime() - periodStart.getTime();
      const newProgress = Math.min(100, Math.max(0, (elapsed / total) * 100));

      // Calculate remaining time in milliseconds
      const remainingTime = Math.max(
        0,
        nextPigeons.getTime() - current.getTime()
      );
      setRemaining(remainingTime);

      // Convert to mm:ss format
      const minutes = Math.floor(remainingTime / 60000);
      const seconds = Math.floor((remainingTime % 60000) / 1000);
      setTimeRemaining(
        `${minutes.toString().padStart(2, "0")}:${seconds
          .toString()
          .padStart(2, "0")}`
      );

      setProgress(newProgress);
    };

    updateProgress();
    const interval = setInterval(updateProgress, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ position: "relative" }}>
      <div
        style={{
          width: "100%",
          height: "20px",
          background: "#eee",
          borderRadius: "10px",
          margin: "20px 0",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${progress}%`,
            height: "100%",
            background: "linear-gradient(90deg, #4CAF50, #8BC34A)",
            transition: "width 0.5s ease-in-out",
          }}
        />
      </div>
      <div
        style={{
          position: "absolute",
          top: "0",
          left: "50%",
          transform: "translateX(-50%)",
          width: "100%",
          fontSize: "14px",
          fontWeight: "bold",
          color: "#333",
        }}
      >
        {remaining <= 0
          ? "New Pigeons Arriving Soon!"
          : `${timeRemaining} remaining`}
      </div>
    </div>
  );
};

export default ProgressBar;
