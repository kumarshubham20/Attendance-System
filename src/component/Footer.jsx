const Footer = () => {
  return (
    <section className="w-full bg-white py-6 text-black px-4">
      <div className="flex flex-col md:flex-row justify-between items-center max-w-7xl mx-auto gap-8">
        {/* Left Section */}
        <div className="text-center md:text-left">
          <h2 className="font-bold text-lg text-black pb-2">TrackAS</h2>
          <p className="text-sm max-w-sm">
            TrackAS is a smart attendance system that allows you to create class
            schedules and take student attendance efficiently.
          </p>
        </div>

        {/* Right Section */}
        <div className="flex flex-col md:flex-row items-center gap-4 md:gap-6 text-center md:text-left">
          <div className="text-xs">
            <p className="pb-2">Open Source Project</p>
            <p className="pb-2">
              It leverages QR codes and geolocation to enable lecturers to
              efficiently take attendance in classes and manage schedules, while
              providing a straightforward attendance process for students.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Footer;
