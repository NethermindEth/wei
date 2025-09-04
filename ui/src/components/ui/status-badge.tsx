import * as React from "react";

type Status = "pass" | "fail" | "warning" | "neutral" | undefined;

interface StatusBadgeProps {
  status?: Status;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  let bgColor = "bg-gray-500";
  const textColor = "text-white";
  let label = "Unknown";

  switch (status) {
    case "pass":
      bgColor = "bg-green-500";
      label = "Pass";
      break;
    case "fail":
      bgColor = "bg-red-500";
      label = "Fail";
      break;
    case "warning":
      bgColor = "bg-amber-500";
      label = "Warning";
      break;
    case "neutral":
      bgColor = "bg-blue-500";
      label = "Neutral";
      break;
    default:
      bgColor = "bg-gray-500";
      label = "Unknown";
  }

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${bgColor} ${textColor}`}
    >
      {label}
    </span>
  );
}
