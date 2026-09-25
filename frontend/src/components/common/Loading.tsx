/** Simple loading spinner with an accessible label, used for async view states. */

interface LoadingProps {
  label?: string;
}

export default function Loading({ label = "Loading..." }: LoadingProps) {
  return (
    <div
      role="status"
      className="flex items-center justify-center gap-3 py-10 text-gray-500"
    >
      <svg
        className="h-5 w-5 animate-spin text-blue-600"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
        />
      </svg>
      <span className="text-sm">{label}</span>
    </div>
  );
}