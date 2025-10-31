import { useState, useEffect, useRef } from 'react';
import { FiMoreVertical } from 'react-icons/fi';

const ActionsDropdown = ({ actions }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const toggleDropdown = () => setIsOpen(!isOpen);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className="actions-dropdown-container" ref={dropdownRef}>
      <button onClick={toggleDropdown} className="actions-dropdown-trigger">
        <FiMoreVertical size={20} />
      </button>
      {isOpen && (
        <div className="actions-dropdown-menu">
          {actions.map((action, index) => (
            <button
              key={index}
              onClick={() => {
                action.onClick();
                setIsOpen(false);
              }}
              className={`actions-dropdown-item ${action.className || ''}`}
            >
              {action.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default ActionsDropdown;