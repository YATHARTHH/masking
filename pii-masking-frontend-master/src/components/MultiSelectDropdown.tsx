import { useState, useRef, useEffect } from "react";

interface MultiSelectDropdownProps {
  categories: string[];
  selected: string[];
  onChange: (values: string[]) => void;
}

const MultiSelectDropdown: React.FC<MultiSelectDropdownProps> = ({
  categories,
  selected,
  onChange,
}) => {
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement | null>(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const toggleValue = (value: string) => {
    if (selected.includes(value)) {
      onChange(selected.filter((v) => v !== value));
    } else {
      onChange([...selected, value]);
    }
  };

  const toggleSelectAll = () => {
    if (selected.length === categories.length) {
      onChange([]); // Unselect all
    } else {
      onChange([...categories]); // Select all
    }
  };

  return (
    <div className="relative w-full" ref={dropdownRef}>
      {/* Display box */}
      <button
        type="button"
        className="w-full max-w-full border border-gray-300 rounded-md px-3 py-2 text-left bg-white focus:ring-2 focus:ring-orange-400 whitespace-nowrap overflow-hidden text-ellipsis"
        onClick={() => setOpen(!open)}
      >
        {selected.length > 0
          ? selected.map((v) => v.replace(/_/g, " ")).join(", ")
          : "Select Categories"}
      </button>

      {/* Dropdown */}
      {open && (
        <div className="absolute z-20 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">

          {/* Select All Option */}
          <label
            className="flex items-center px-3 py-2 hover:bg-gray-100 cursor-pointer border-b border-gray-200"
          >
            <input
              type="checkbox"
              className="mr-2"
              checked={selected.length === categories.length}
              onChange={toggleSelectAll}
            />
            <span className="font-semibold">Select All</span>
          </label>

          {/* Individual items */}
          {categories.map((item) => (
            <label
              key={item}
              className="flex items-center px-3 py-2 hover:bg-gray-100 cursor-pointer"
            >
              <input
                type="checkbox"
                className="mr-2"
                checked={selected.includes(item)}
                onChange={() => toggleValue(item)}
              />
              <span className="capitalize">{item.replace(/_/g, " ")}</span>
            </label>
          ))}
        </div>
      )}
    </div>
  );
};

export default MultiSelectDropdown;
