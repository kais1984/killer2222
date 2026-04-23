import { Component, ErrorInfo, ReactNode } from "react";
import { Link } from "react-router-dom";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-background px-6">
          <div className="text-center max-w-md">
            <h1 className="font-heading text-4xl mb-4">Something Went Wrong</h1>
            <p className="font-body text-sm text-muted-foreground mb-8">
              We're sorry, but something unexpected happened. Please try refreshing the page.
            </p>
            <Link to="/" className="btn-luxury">Return Home</Link>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
