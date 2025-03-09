import React from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { ArrowRight, CheckCircle, Facebook, Instagram, Twitter, ShoppingCart, Zap, Globe, BarChart, Menu } from 'lucide-react'
import { Link } from 'react-router-dom';
import { SignedIn, SignedOut, useAuth } from "@clerk/clerk-react";
import { useNavigate } from "react-router-dom";
import {
  enable as enableDarkMode,
  disable as disableDarkMode,
  exportGeneratedCSS as collectCSS,
  isEnabled as isDarkReaderEnabled,
} from 'darkreader';
import { useState } from "react"


const Home: React.FC = () => {
  const { signOut } = useAuth();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);

  const handleGetStarted = () => {
    navigate("/dashboard"); // Redirect to /dashboard route
  };

  const handleSignOut = () => {
    signOut();
  };

  const handleDashboardClick = () => {
    navigate("/dashboard");
  };

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

      // Dark mode function
      const [darkMode, setDarkMode] = useState(false);
  
      const toggleDarkMode = () => {
          if (darkMode) {
              enableDarkMode({
                  brightness: 100,
                  contrast: 90,
                  sepia: 10,
              });
          } else {
              disableDarkMode();
          }
          setDarkMode(!darkMode);
      };
  
      const handleCollectCSS = async () => {
          const css = await collectCSS();
          console.log(css); // Log or handle the generated CSS
      };
  
      const checkDarkModeStatus = () => {
          const isEnabled = isDarkReaderEnabled();
          console.log('Is Dark Mode enabled:', isEnabled);
      };

  return (
    <div className="flex flex-col min-h-screen bg-white text-blue-900">
      <header className="px-4 lg:px-6 h-16 flex items-center border-b border-blue-200">
        <Link className="flex items-center justify-center" to="#">
          <ShoppingCart className="h-6 w-6 text-blue-600" />
          <span className="ml-2 text-xl font-bold text-blue-600">SellSmart AI</span>
        </Link>
        <nav className={`ml-auto ${isMenuOpen ? 'flex' : 'hidden'} md:flex flex-col md:flex-row absolute md:relative top-16 md:top-0 left-0 right-0 bg-white md:bg-transparent z-50 md:z-auto gap-4 p-4 md:p-0 md:h-16 md:items-center`}>
        <div className="btn d-inline-flex align-items-center justify-content-center shadow-sm rounded-full">
                                        <button onClick={toggleDarkMode}>
                                            {darkMode ? (
                                                <img
                                                    src="https://cdn-icons-png.flaticon.com/256/4445/4445942.png"
                                                    alt=""
                                                    className="w-8 h-8 rounded-full"
                                                />
                                            ) : (
                                                <img
                                                    src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT_xqmYro3MAiVCYxvtXyjyx_MC4VYmNKVRqQ&s"
                                                    alt=""
                                                    className="w-8 h-8 rounded-full"
                                                />
                                            )}
                                        </button>

                                        <button onClick={handleCollectCSS}></button>
                                        <button onClick={checkDarkModeStatus}></button>

                                        {/* Optionally display the collected CSS */}
                                        {/* <pre>{collectedCSS}</pre> */}
                                    </div>
          <Link className="text-sm font-medium hover:text-blue-600 hover:underline underline-offset-4" to="#features">
            Features
          </Link>
          <Link className="text-sm font-medium hover:text-blue-600 hover:underline underline-offset-4" to="#how-it-works">
            How It Works
          </Link>
          <Link className="text-sm font-medium hover:text-blue-600 hover:underline underline-offset-4" to="#pricing">
            Pricing
          </Link>
          <Link className="text-sm font-medium hover:text-blue-600 hover:underline underline-offset-4" to="#contact">
            Contact
          </Link>
          <SignedIn>
            <Button onClick={handleSignOut} className="bg-red-600 text-white hover:bg-red-700">
              Sign Out
            </Button>
            <Button 
              className="bg-blue-600 text-white hover:bg-blue-700" 
              onClick={handleDashboardClick}
            >
              Dashboard
            </Button>
          </SignedIn>
        </nav>
        <Button className="ml-auto md:hidden h-10 w-10" variant="ghost" size="icon" onClick={toggleMenu}>
          <Menu className="h-6 w-6" />
        </Button>
      </header>
      <main className="flex-1">
        <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48 bg-blue-50">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none text-blue-600">
                  From Social Media to Ecommerce Listings in Minutes
                </h1>
                <p className="mx-auto max-w-[700px] text-blue-800 md:text-xl dark:text-blue-200">
                  Automatically create Ecommerce listings from your social media profiles using AI. Streamline your e-commerce business today.
                </p>
              </div>
              <SignedOut>
                <div className="space-x-4">
                  <Button onClick={handleGetStarted} className="bg-blue-600 text-white hover:bg-blue-700">
                    Get Started
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </div>
              </SignedOut>
            </div>
          </div>
        </section>
        <section id="features" className="w-full py-12 md:py-24 lg:py-32 bg-white">
          <div className="container px-4 md:px-6">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl text-center mb-12 text-blue-600">Features</h2>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 lg:gap-12">
              <Card className="bg-blue-50 border-blue-200">
                <CardHeader>
                  <Zap className="h-8 w-8 mb-2 text-blue-600" />
                  <CardTitle className="text-blue-600">AI-Powered Listings</CardTitle>
                </CardHeader>
                <CardContent>Generate optimized Ecommerce listings using advanced AI technology.</CardContent>
              </Card>
              <Card className="bg-blue-50 border-blue-200">
                <CardHeader>
                  <Globe className="h-8 w-8 mb-2 text-blue-600" />
                  <CardTitle className="text-blue-600">Multi-Platform Support</CardTitle>
                </CardHeader>
                <CardContent>Connect and monitor multiple social media profiles in one place.</CardContent>
              </Card>
              <Card className="bg-blue-50 border-blue-200">
                <CardHeader>
                  <BarChart className="h-8 w-8 mb-2 text-blue-600" />
                  <CardTitle className="text-blue-600">Automated Monitoring</CardTitle>
                </CardHeader>
                <CardContent>Stay updated with real-time monitoring of your social media content.</CardContent>
              </Card>
            </div>
          </div>
        </section>
        <section id="how-it-works" className="w-full py-12 md:py-24 lg:py-32 bg-blue-50">
          <div className="container px-4 md:px-6">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl text-center mb-12 text-blue-600">How It Works</h2>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 lg:gap-12">
              <div className="flex flex-col items-center text-center">
                <div className="mb-4 text-4xl font-bold text-blue-600">1</div>
                <h3 className="text-xl font-bold mb-2 text-blue-800">Connect Your Profiles</h3>
                <p className="text-blue-600">Link your social media accounts to our platform.</p>
                <div className="mt-4 flex space-x-2">
                  <Facebook className="h-8 w-8 text-blue-600" />
                  <Instagram className="h-8 w-8 text-blue-600" />
                  <Twitter className="h-8 w-8 text-blue-600" />
                </div>
              </div>
              <div className="flex flex-col items-center text-center">
                <div className="mb-4 text-4xl font-bold text-blue-600">2</div>
                <h3 className="text-xl font-bold mb-2 text-blue-800">AI Analysis</h3>
                <p className="text-blue-600">Our AI analyzes your content and creates optimized listings.</p>
                <Zap className="mt-4 h-12 w-12 text-blue-600" />
              </div>
              <div className="flex flex-col items-center text-center">
                <div className="mb-4 text-4xl font-bold text-blue-600">3</div>
                <h3 className="text-xl font-bold mb-2 text-blue-800">List on Ecommerce</h3>
                <p className="text-blue-600">Approve and publish your new listings on Flipkart, Amazon, Meesho, etc with one click.</p>
                <ShoppingCart className="mt-4 h-12 w-12 text-blue-600" />
              </div>
            </div>
          </div>
        </section>
        <section className="w-full py-12 md:py-24 lg:py-32 bg-white">
          <div className="container px-4 md:px-6">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl text-center mb-12 text-blue-600">Testimonials</h2>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 lg:gap-12">
              <Card className="bg-blue-50 border-blue-200">
                <CardHeader>
                  <div className="flex items-center space-x-4">
                    <Avatar>
                      <AvatarImage src="/placeholder.svg?height=40&width=40" alt="@johndoe" />
                      <AvatarFallback>JD</AvatarFallback>
                    </Avatar>
                    <div>
                      <CardTitle className="text-blue-600">John Doe</CardTitle>
                      <CardDescription>Social Media Influencer</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  "This app has revolutionized how I manage my e-commerce business. It's a game-changer!"
                </CardContent>
              </Card>
              <Card className="bg-blue-50 border-blue-200">
                <CardHeader>
                  <div className="flex items-center space-x-4">
                    <Avatar>
                      <AvatarImage src="/placeholder.svg?height=40&width=40" alt="@janedoe" />
                      <AvatarFallback>JD</AvatarFallback>
                    </Avatar>
                    <div>
                      <CardTitle className="text-blue-600">Jane Doe</CardTitle>
                      <CardDescription>Small Business Owner</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  "The AI-generated listings are spot-on. It's like having a team of experts working for me 24/7."
                </CardContent>
              </Card>
              <Card className="bg-blue-50 border-blue-200">
                <CardHeader>
                  <div className="flex items-center space-x-4">
                    <Avatar>
                      <AvatarImage src="/placeholder.svg?height=40&width=40" alt="@alexsmith" />
                      <AvatarFallback>AS</AvatarFallback>
                    </Avatar>
                    <div>
                      <CardTitle className="text-blue-600">Alex Smith</CardTitle>
                      <CardDescription>E-commerce Entrepreneur</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  "The time I save with this app allows me to focus on growing my business. Highly recommended!"
                </CardContent>
              </Card>
            </div>
          </div>
        </section>
        <section id="pricing" className="w-full py-12 md:py-24 lg:py-32 bg-blue-50">
          <div className="container px-4 md:px-6">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl text-center mb-12 text-blue-600">Pricing Plans</h2>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 lg:gap-12">
              <Card>
                <CardHeader>
                  <CardTitle className="text-blue-600">Basic</CardTitle>
                  <CardDescription>For small businesses</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold mb-2 text-blue-600">$29/mo</div>
                  <ul className="space-y-2">
                    <li className="flex items-center"><CheckCircle className="mr-2 h-4 w-4 text-blue-600" /> 1 Social Media Account</li>
                    <li className="flex items-center"><CheckCircle className="mr-2 h-4 w-4 text-blue-600" /> 50 Listings/month</li>
                    <li className="flex items-center"><CheckCircle className="mr-2 h-4 w-4 text-blue-600" /> Basic AI Analysis</li>
                  </ul>
                </CardContent>
                <CardFooter>
                  <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white-100">Choose Plan</Button>
                </CardFooter>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle className="text-blue-600">Pro</CardTitle>
                  <CardDescription>For growing businesses</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold mb-2 text-blue-600">$79/mo</div>
                  <ul className="space-y-2">
                    <li className="flex items-center"><CheckCircle className="mr-2 h-4 w-4 text-blue-600" /> 3 Social Media Accounts</li>
                    <li className="flex items-center"><CheckCircle className="mr-2 h-4 w-4 text-blue-600" /> 200 Listings/month</li>
                    <li className="flex items-center"><CheckCircle className="mr-2 h-4 w-4 text-blue-600" /> Advanced AI Analysis</li>
                  </ul>
                </CardContent>
                <CardFooter>
                  <Button className="w-full bg-blue-600 hover:bg-blue-700">Choose Plan</Button>
                </CardFooter>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle className="text-blue-600">Enterprise</CardTitle>
                  <CardDescription>For large businesses</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold mb-2 text-blue-600">Custom
</div>
                  <ul className="space-y-2">
                    <li className="flex items-center"><CheckCircle className="mr-2 h-4 w-4 text-blue-600" /> Unlimited Social Media Accounts</li>
                    <li className="flex items-center"><CheckCircle className="mr-2 h-4 w-4 text-blue-600" /> Unlimited Listings</li>
                    <li className="flex items-center"><CheckCircle className="mr-2 h-4 w-4 text-blue-600" /> Custom AI Solutions</li>
                  </ul>
                </CardContent>
                <CardFooter>
                  <Button className="w-full bg-blue-600 hover:bg-blue-700">Contact Sales</Button>
                </CardFooter>
              </Card>
            </div>
          </div>
        </section>
        <section className="w-full py-12 md:py-24 lg:py-32 bg-blue-600 text-white">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="space-y-2">
                <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl text-blue-100">Ready to Streamline Your E-commerce?</h2>
                <p className="mx-auto max-w-[600px] text-blue-100 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                  Join thousands of successful sellers who have transformed their business with our AI-powered platform.
                </p>
              </div>
              <Button className="bg-white text-blue-600 hover:bg-blue-50" size="lg">
                Get Started Now
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </div>
          </div>
        </section>
      </main>
      <footer className="flex flex-col gap-2 sm:flex-row py-6 w-full shrink-0 items-center px-4 md:px-6 border-t border-blue-200">
        <p className="text-xs text-blue-600">© 2025 SellSmart AI. All rights reserved.</p>
        <nav className="sm:ml-auto flex gap-4 sm:gap-6">
          <Link className="text-xs hover:underline underline-offset-4 text-blue-600" to="#">
            Terms of Service
          </Link>
          <Link className="text-xs hover:underline underline-offset-4 text-blue-600" to="#">
            Privacy
          </Link>
        </nav>
      </footer>
    </div>
  )
}

export default Home

