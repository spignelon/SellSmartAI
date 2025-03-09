import React from 'react'

function Sidebar() {
  return (
    <>
    {/* preload section-menu-left  */}
    <div className="section-menu-left">
                    <div className="box-logo">
                        <a href="index.html" id="site-logo-inner">
                            <img className="" id="logo_header" alt="" src="images/logo/logo.png" data-light="images/logo/logo.png" data-dark="images/logo/logo-dark.png" />
                        </a>
                        <div className="button-show-hide">
                            <i className="icon-menu-left"></i>
                        </div>
                    </div>
                    <div className="center">
                        <div className="center-item">
                            <ul className="menu-list">
                                <li className="menu-item">
                                <a href="/dashboard" className="menu-item-button">
                                    <div className="icon"><i className="icon-grid"></i></div>
                                    <div className="text">Dashboard</div>
                                </a>
                                </li>
                                <li className="menu-item">
                                    <a href="gallery.html" className="">
                                        <div className="icon"><i className="icon-image"></i></div>
                                        <div className="text">Link Social Media</div>
                                    </a>
                                </li>
                                <li className="menu-item">
                                    <a href="report.html" className="">
                                        <div className="icon"><i className="icon-pie-chart"></i></div>
                                        <div className="text">Generated Listings</div>
                                    </a>
                                </li>
                                <li className="menu-item">
                                    <a href="setting.html" className="">
                                        <div className="icon"><i className="icon-settings"></i></div>
                                        <div className="text">Setting</div>
                                    </a>
                                </li>
                                <li className="menu-item">
                                    <a href="#" className="">
                                        <div className="icon"><i className="icon-help-circle"></i></div>
                                        <div className="text">Help center</div>
                                    </a>
                                </li>
                            </ul>
                        </div>
                    </div>

                </div>
                {/* section-menu-left  */}
    </>
  )
}

export default Sidebar