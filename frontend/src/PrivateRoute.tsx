import React from "react";
import { SignedIn, SignedOut, RedirectToSignIn } from "@clerk/clerk-react";  // Clerk's auth hook

interface PrivateRouteProps {
  element: React.ReactNode;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ element }) => {
  return <>
        <SignedOut>
        <RedirectToSignIn />
        </SignedOut>
        <SignedIn>
        {element}
    </SignedIn>
    </>; // Return the page component if signed in
};

export default PrivateRoute;
