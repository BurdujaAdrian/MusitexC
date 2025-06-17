import React, { useEffect, useState } from "react";

export default function FastApiConnectionTest() {
  const [message, setMessage] = useState("Connecting...");

  useEffect(() => {
    fetch("http://localhost:8000/api/ping")
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch((err) => setMessage("Error: " + err.message));
  }, []);

  return (
    <div>
      <h2>FastAPI Connection Test</h2>
      <p>{message}</p>
    </div>
  );
}