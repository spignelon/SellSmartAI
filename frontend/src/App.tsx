import "./App.css";
import { SignedIn, SignedOut, SignInButton, useAuth } from "@clerk/clerk-react";

function App() {
  const { isLoaded, getToken, signOut } = useAuth();

  // Update your fetch function to handle auth errors
  const makeAuthenticatedRequest = async (url: string, options = {}) => {
    try {
      const token = await getToken();
      const response = await fetch(
        `${import.meta.env.VITE_BACKEND_API_URL}${url}`,
        {
          ...options,
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
            ...options.headers,
          },
        }
      );
      
      if (response.status === 403) {
        console.error("Authentication error: Forbidden");
        // Handle forbidden error - could sign out or redirect
        // signOut();
        // Or just log it during development:
        console.log("Dev mode: Authentication would normally fail here");
      }
      
      return await response.json();
    } catch (error) {
      console.error("Request failed:", error);
      return { error: "Request failed" };
    }
  };

  // Use this function for your API calls
  const getAllPosts = async () => {
    const data = await makeAuthenticatedRequest("/posts");
    console.log(data);
  };

  return (
    <div className="w-full h-screen">
      <h1 className="text-center">Clerk Django</h1>
      {isLoaded ? (
        <>
          <SignedOut>
            <SignInButton />
          </SignedOut>
          <SignedIn>
            <p>
              You have been logged in successfully. <br /> Click the button to
              initate an api call with django which returns some data.
            </p>
            <button className="" onClick={getAllPosts}>
              Click Here
            </button>
            <br />
            <br />
            <div>
              <span className="" onClick={() => signOut()}>
                Logout
              </span>
            </div>
          </SignedIn>
        </>
      ) : (
        <span>Loading ...</span>
      )}
    </div>
  );
}

export default App;
