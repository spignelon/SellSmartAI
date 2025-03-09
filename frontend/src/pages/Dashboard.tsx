import React, { useState, useEffect } from "react";
import { useAuth } from "@clerk/clerk-react";
import { Link } from 'react-router-dom';
import { Pie } from "react-chartjs-2";
import {
    Chart as ChartJS,
    ArcElement,
    Tooltip,
    Legend,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);
import { Line } from "react-chartjs-2";
import {
    enable as enableDarkMode,
    disable as disableDarkMode,
    exportGeneratedCSS as collectCSS,
    isEnabled as isDarkReaderEnabled,
} from 'darkreader';


// Register chart components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

// Define the interface for ProductData
interface ProductData {
    product_id: string;
    created_at: string;
    images_list: string[];
    product_title: string;
    price: string;
    product_details: Record<string, any>;
    about_this_item: string;
    product_description: string;
    updated_at: string;
    approved: boolean;
}


const Dashboard: React.FC = () => {
    const { isLoaded, getToken, signOut } = useAuth();
    const [helloUser, setHelloUser] = useState(""); // State to store the hello user message
    const [error, setError] = useState(null); // State to handle errors
    const [profile_img, setProfileImg] = useState(null); // State to store the profile image

    // State to track whether the window is maximized or not
    const [isMaximized, setIsMaximized] = useState<boolean>(false);

    // Handle the button click to toggle the maximize state
    const handleMaximizeClick = () => {
        if (isMaximized) {
            document.exitFullscreen();
        } else {
            const elem = document.documentElement;
            if (elem.requestFullscreen) {
                elem.requestFullscreen();
            }
        }
        setIsMaximized((prevState) => !prevState);
    };

    // Function to fetch user data.
    const getUsername = async () => {
        try {
            const token = await getToken();
            const response = await fetch(
                `${import.meta.env.VITE_BACKEND_API_URL}/profile_data`,
                {
                    method: "GET",
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json",
                    },
                }
            );
            if (!response.ok) {
                throw new Error("Failed to fetch data");
            }
            const data = await response.json();
            if (data.first_name) {
                setHelloUser(data.first_name); // Update state with API response
                setProfileImg(data.profile_image); // Update state with API response
            } else {
                setError(data.message || "Unknown error occurred");
            }
        } catch (err: any) {
            setError(err.message);
        }
    };

    // Fetch Dashboard stats
    const [dashboardStats, setDashboardStats] = useState({
        total_listings: "Loading...",
        approved_listings: "Loading...",
        disapproved_listings: "Loading...",
        connected_social_media: 0,
    });

    // Function to fetch dashboard stats.
    const fetchDashboardStats = async () => {
        try {
            const token = await getToken();
            const response = await fetch(`${import.meta.env.VITE_BACKEND_API_URL}/dashboard_stats`, {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
            });
            if (!response.ok) {
                throw new Error("Failed to fetch dashboard stats");
            }
            const data = await response.json();
            setDashboardStats({
                total_listings: data.total_listings || 0,
                approved_listings: data.approved_listings || 0,
                disapproved_listings: data.disapproved_listings || 0,
                connected_social_media: data.connected_social_media || 0,
            });
        } catch (err: any) {
            setError(err.message);
        }
    };

    // Fetch user data when the component mounts
    useEffect(() => {
        if (isLoaded) {
            getUsername();
            fetchDashboardStats();
        }
    }, [isLoaded]);

    // Data for the pie charts
    const listingsChartData = {
        labels: ["Approved Listings", "Disapproved Listings"],
        datasets: [
            {
                data: [
                    dashboardStats.approved_listings,
                    dashboardStats.disapproved_listings,
                ],
                backgroundColor: ["#36A2EB", "#FF6384"],
                hoverBackgroundColor: ["#36A2EB", "#FF6384"],
            },
        ],
    };

    const socialMediaChartData = {
        labels: ["Connected", "Not Connected"],
        datasets: [
            {
                data: [
                    dashboardStats.connected_social_media || 0,
                    3 - dashboardStats.connected_social_media || 0, // Assuming total is 3
                ],
                backgroundColor: ["#4BC0C0", "#FFCE56"],
                hoverBackgroundColor: ["#4BC0C0", "#FFCE56"],
            },
        ],
    };

    // Function for Line graph

    const [productList, setProductList] = useState<ProductData[]>([]);
    const [isProductListLoaded, setIsProductListLoaded] = useState<boolean>(false);

    const fetchPreviousListings = async () => {
        try {
            const token = await getToken(); // Replace with your authentication method
            const response = await fetch(
                `${import.meta.env.VITE_BACKEND_API_URL}/previous_listing_data`,
                {
                    method: "GET",
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json",
                    },
                }
            );

            if (!response.ok) {
                throw new Error("Failed to fetch product listings");
            }

            const data = await response.json();
            setProductList(data);
            setIsProductListLoaded(true);
        } catch (err: any) {
            setError(err.message);
        }
    };

    useEffect(() => {
        fetchPreviousListings();
    }, []);

    // Process data to count listings per day
    const processData = () => {
        const listingsPerDay: Record<string, number> = {};

        productList.forEach((product) => {
            const date = new Date(product.updated_at).toLocaleDateString(); // Extract date from updated_at
            listingsPerDay[date] = (listingsPerDay[date] || 0) + 1;
        });

        // Convert the data into chart-friendly format
        const labels = Object.keys(listingsPerDay).reverse();
        const data = Object.values(listingsPerDay).reverse();

        return {
            labels,
            data,
        };
    };

    // Prepare chart data
    const { labels, data } = processData();

    // Chart options
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: "top" as const, // Explicitly specify the valid string literal type
            },
            title: {
                display: true,
                text: "Listings Over Time",
            },
            scales: {
                x: {
                    reverse: true, // Reverse the X-axis to display from latest to oldest
                },
            },
        },
    };

    // Chart data
    const chartData = {
        labels,
        datasets: [
            {
                label: "Product Listings",
                data,
                borderColor: "rgba(75, 192, 192, 1)",
                backgroundColor: "rgba(75, 192, 192, 0.2)",
                borderWidth: 1,
            },
        ],
    };

    // Dark mode function
    const [darkMode, setDarkMode] = useState(false);

    useEffect(() => {
        // Automatically follow the system color scheme

    }, []);

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
        <>
            <div id="wrapper">
                <div id="page" className="">
                    <div className="layout-wrap">
                        <div className="section-menu-left dark-sidebar">
                            <div className="box-logo">
                                <Link to="#" id="site-logo-inner">
                                    <img className="logo" src="images\logo\logo.png" alt="" />
                                </Link>
                                <div className="button-show-hide">
                                    <i className="icon-menu-left"></i>
                                </div>
                            </div>
                            <div className="center">
                                <div className="center-item">
                                    <ul className="menu-list">
                                        <li className="menu-item">
                                            <Link to="/" className="menu-item-button">
                                                <div className="icon"><i className="icon-home"></i></div>
                                                <div className="text">Home</div>
                                            </Link>
                                        </li>
                                        <li className="menu-item">
                                            <Link to="/dashboard" className="menu-item-button">
                                                <div className="icon"><i className="icon-grid"></i></div>
                                                <div className="text">Dashboard</div>
                                            </Link>
                                        </li>
                                        <li className="menu-item">
                                            <Link to="/linksocialmedia" className="">
                                                <div className="icon"><i className="icon-image"></i></div>
                                                <div className="text">Link Social Media</div>
                                            </Link>
                                        </li>
                                    </ul>
                                </div>
                            </div>

                        </div>
                        {/* section-menu-left  */}
                        {/* section-content-right  */}
                        <div className="section-content-right">
                            {/* header-dashboard  */}
                            <div className="header-dashboard dark-header">
                                <div className="wrap">
                                    <div className="header-left">
                                        <Link to="index.html">
                                            <img className="logo" src="images/logo/logo.png" />
                                        </Link>
                                        <div className="button-show-hide">
                                            <i className="icon-menu-left"></i>
                                        </div>
                                    </div>
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
                                    <div className="header-grid">
                                        <div className="header-item button-zoom-maximize" onClick={handleMaximizeClick}>
                                            <div className="">
                                                <i className={`icon-maximize ${isMaximized ? 'maximized' : ''}`}></i>
                                            </div>
                                        </div>
                                        <div className="popup-wrap user type-header">
                                            <div className="dropdown">
                                                <button className="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton3" data-bs-toggle="dropdown" aria-expanded="false">
                                                    <span className="header-user wg-user">
                                                        <span className="image">
                                                            {profile_img && <img src={profile_img} alt="" />}
                                                            {error && <img src="images/avatar/user-1.png" alt="" />}
                                                        </span>
                                                        <span className="flex flex-column">
                                                            <span className="text-tiny">Hello</span>
                                                            {helloUser && <span className="body-title mb-2">{helloUser}!</span>}
                                                            {error && <span className="body-title mb-2">Error: {error}!</span>}
                                                        </span>
                                                    </span>
                                                </button>
                                                <ul className="dropdown-menu dropdown-menu-end has-content" aria-labelledby="dropdownMenuButton3" >
                                                    <li>
                                                        <Link to="#" className="user-item">
                                                            <div className="icon">
                                                                <i className="icon-user"></i>
                                                            </div>
                                                            <div className="body-title-2">Account</div>
                                                        </Link>
                                                    </li>
                                                    <li>
                                                        <Link to="#" className="user-item">
                                                            <div className="icon">
                                                                <i className="icon-log-out"></i>
                                                            </div>
                                                            <div className="body-title-2" onClick={() => signOut()}>Log out</div>
                                                        </Link>
                                                    </li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            {/* header-dashboard  */}
                            {/* main-content  */}
                            <div className="main-content main-content-dark">
                                {/* main-content-wrap  */}
                                <div className="main-content-inner">
                                    {/* main-content-wrap  */}
                                    <div className="main-content-wrap">
                                        <div className="tf-section-4 mb-30">
                                            {error && <div className="error-message">{error}</div>}
                                            {/* Total Listings */}
                                            <div className="wg-chart-default">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center gap14">
                                                        <div className="image type-white">
                                                            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="52" viewBox="0 0 48 52" fill="none">
                                                                <path d="M19.1094 2.12943C22.2034 0.343099 26.0154 0.343099 29.1094 2.12943L42.4921 9.85592C45.5861 11.6423 47.4921 14.9435 47.4921 18.5162V33.9692C47.4921 37.5418 45.5861 40.8431 42.4921 42.6294L29.1094 50.3559C26.0154 52.1423 22.2034 52.1423 19.1094 50.3559L5.72669 42.6294C2.63268 40.8431 0.726688 37.5418 0.726688 33.9692V18.5162C0.726688 14.9435 2.63268 11.6423 5.72669 9.85592L19.1094 2.12943Z" fill="#22C55E" />
                                                            </svg>
                                                            <i className="icon-shopping-bag"></i>
                                                        </div>
                                                        <div>
                                                            <div className="body-text mb-2">Total Listings</div>
                                                            <h4>{dashboardStats.total_listings}</h4>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                            {/* Approved Listings */}
                                            <div className="wg-chart-default">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center gap14">
                                                        <div className="image type-white">
                                                            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="52" viewBox="0 0 48 52" fill="none">
                                                                <path d="M19.1094 2.12943C22.2034 0.343099 26.0154 0.343099 29.1094 2.12943L42.4921 9.85592C45.5861 11.6423 47.4921 14.9435 47.4921 18.5162V33.9692C47.4921 37.5418 45.5861 40.8431 42.4921 42.6294L29.1094 50.3559C26.0154 52.1423 22.2034 52.1423 19.1094 50.3559L5.72669 42.6294C2.63268 40.8431 0.726688 37.5418 0.726688 33.9692V18.5162C0.726688 14.9435 2.63268 11.6423 5.72669 9.85592L19.1094 2.12943Z" fill="#FF5200" />
                                                            </svg>
                                                            <i className="icon-dollar-sign"></i>
                                                        </div>
                                                        <div>
                                                            <div className="body-text mb-2">Approved Listings</div>
                                                            <h4>{dashboardStats.approved_listings}</h4>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                            {/* Disapproved Listings */}
                                            <div className="wg-chart-default">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center gap14">
                                                        <div className="image type-white">
                                                            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="52" viewBox="0 0 48 52" fill="none">
                                                                <path d="M19.1094 2.12943C22.2034 0.343099 26.0154 0.343099 29.1094 2.12943L42.4921 9.85592C45.5861 11.6423 47.4921 14.9435 47.4921 18.5162V33.9692C47.4921 37.5418 45.5861 40.8431 42.4921 42.6294L29.1094 50.3559C26.0154 52.1423 22.2034 52.1423 19.1094 50.3559L5.72669 42.6294C2.63268 40.8431 0.726688 37.5418 0.726688 33.9692V18.5162C0.726688 14.9435 2.63268 11.6423 5.72669 9.85592L19.1094 2.12943Z" fill="#CBD5E1" />
                                                            </svg>
                                                            <i className="icon-file"></i>
                                                        </div>
                                                        <div>
                                                            <div className="body-text mb-2">Disapproved Listings</div>
                                                            <h4>{dashboardStats.disapproved_listings}</h4>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                            {/* Connected Social Media */}
                                            <div className="wg-chart-default">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center gap14">
                                                        <div className="image type-white">
                                                            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="52" viewBox="0 0 48 52" fill="none">
                                                                <path d="M19.1094 2.12943C22.2034 0.343099 26.0154 0.343099 29.1094 2.12943L42.4921 9.85592C45.5861 11.6423 47.4921 14.9435 47.4921 18.5162V33.9692C47.4921 37.5418 45.5861 40.8431 42.4921 42.6294L29.1094 50.3559C26.0154 52.1423 22.2034 52.1423 19.1094 50.3559L5.72669 42.6294C2.63268 40.8431 0.726688 37.5418 0.726688 33.9692V18.5162C0.726688 14.9435 2.63268 11.6423 5.72669 9.85592L19.1094 2.12943Z" fill="#2377FC" />
                                                            </svg>
                                                            <i className="icon-users"></i>
                                                        </div>
                                                        <div>
                                                            <div className="body-text mb-2">Connected Social Media</div>
                                                            <h4>{dashboardStats.connected_social_media}</h4>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Dashboard Stats Graph */}
                                        <div className="wg-box mb-30" style={{ height: "400px" }}>
                                            {error && <div>Error: {error}</div>}
                                            {isProductListLoaded ? (
                                                <Line data={chartData} options={options} />
                                            ) : (
                                                <div className="flex justify-center items-center h-full">
                                                    <span className="loader inline-block w-8 h-8 border-4 border-t-4 border-blue-500 border-solid rounded-full animate-spin"></span>
                                                </div>
                                            )}
                                        </div>

                                        <div className="wg-box mb-30">
                                            {error && <p className="error">{error}</p>}
                                            <div style={{ display: "flex", justifyContent: "space-evenly" }}>
                                                <div style={{ width: "30%" }}>
                                                    <h3>Listings Overview</h3>
                                                    <Pie data={listingsChartData} />
                                                </div>
                                                <div style={{ width: "30%" }}>
                                                    <h3>Social Media Connections</h3>
                                                    <Pie data={socialMediaChartData} />
                                                </div>
                                            </div>
                                        </div>

                                        {/* Recently viewed  */}

                                        {/* main-content-wrap  */}
                                    </div>
                                    {/* main-content-wrap  */}
                                    {/* bottom-page  */}
                                    <div className="bottom-page">
                                        <div className="body-text">Made</div>
                                        {/* <i className="icon-heart"></i> */}
                                        <div className="body-text">by: <Link to="#">Ujjawal and Arushi.</Link> All rights reserved.</div>
                                    </div>
                                    {/* bottom-page  */}
                                </div>
                                {/* main-content  */}
                            </div>
                            {/* section-content-right  */}
                        </div>
                        {/* layout-wrap  */}
                    </div>
                    {/* page  */}
                </div>
            </div>
        </>
    );
};

export default Dashboard;
