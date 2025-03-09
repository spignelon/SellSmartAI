import React from 'react';
import { Link } from 'react-router-dom';

const Sidebar: React.FC = () => {
  return (
    <div className="section-menu-left">
      <div className="box-logo">
        <Link to="/" id="site-logo-inner">
          <img src="/images/logo/logo.png" alt="Logo" width={154} height={52} />
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
                <div className="icon"><i className="icon-grid"></i></div>
                <div className="text">Dashboard</div>
              </Link>
            </li>
            <li className="menu-item">
              <Link to="/gallery" className="">
                <div className="icon"><i className="icon-image"></i></div>
                <div className="text">Link Social Media</div>
              </Link>
            </li>
            <li className="menu-item">
              <Link to="/report" className="">
                <div className="icon"><i className="icon-pie-chart"></i></div>
                <div className="text">Generated Listings</div>
              </Link>
            </li>
            <li className="menu-item">
              <Link to="/setting" className="">
                <div className="icon"><i className="icon-settings"></i></div>
                <div className="text">Setting</div>
              </Link>
            </li>
            <li className="menu-item">
              <Link to="/help" className="">
                <div className="icon"><i className="icon-help-circle"></i></div>
                <div className="text">Help center</div>
              </Link>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
