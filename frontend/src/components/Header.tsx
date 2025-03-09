import React from 'react';

const Header: React.FC = () => {
  return (
    <div className="header-dashboard">
      <div className="wrap">
        <div className="header-left">
          <a href="/">
            <img src="/images/logo/logo.png" alt="Logo" width={154} height={52} id="logo_header_mobile" />
          </a>
          <div className="button-show-hide">
            <i className="icon-menu-left"></i>
          </div>
          <form className="form-search flex-grow">
            <fieldset className="name">
              <input type="text" placeholder="Search here..." className="show-search" name="name" tabIndex={2} required />
            </fieldset>
            <div className="button-submit">
              <button type="submit"><i className="icon-search"></i></button>
            </div>
          </form>
        </div>
        <div className="header-grid">
          <div className="header-item button-zoom-maximize">
            <div className="">
              <i className="icon-maximize"></i>
            </div>
          </div>
          <div className="popup-wrap user type-header">
            <div className="dropdown">
              <button className="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton3" data-bs-toggle="dropdown" aria-expanded="false">
                <span className="header-user wg-user">
                  <span className="image">
                    <img src="/images/avatar/user-1.png" alt="User Avatar" width={40} height={40} />
                  </span>
                  <span className="flex flex-column">
                    <span className="body-title mb-2">Kristin Watson</span>
                    <span className="text-tiny">Admin</span>
                  </span>
                </span>
              </button>
              <ul className="dropdown-menu dropdown-menu-end has-content" aria-labelledby="dropdownMenuButton3">
                <li>
                  <a href="#" className="user-item">
                    <div className="icon">
                      <i className="icon-user"></i>
                    </div>
                    <div className="body-title-2">Account</div>
                  </a>
                </li>
                <li>
                  <a href="/login" className="user-item">
                    <div className="icon">
                      <i className="icon-log-out"></i>
                    </div>
                    <div className="body-title-2">Log out</div>
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Header;
