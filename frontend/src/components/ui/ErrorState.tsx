/**
 * Error state component with retry option.
 * Componente de estado de erro com opcao de tentar novamente.
 */

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export default function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4">
      <p className="text-sm text-red-700">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-2 text-sm font-medium text-red-600 hover:text-red-800 hover:underline"
        >
          Try again / Tentar novamente
        </button>
      )}
    </div>
  );
}
