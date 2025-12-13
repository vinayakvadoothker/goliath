import centraLogoImg from "figma:asset/13e993af34fe65754cbc14c91a3cdb0b4df127d6.png";

export function CentraLogo() {
  return (
    <div className="flex flex-col items-center gap-3">
      <div className="w-16 h-16 flex items-center justify-center">
        <img 
          src={centraLogoImg} 
          alt="Centra Logo"
          className="w-full h-full object-contain"
        />
      </div>
      <span className="text-white text-xl tracking-wider">CENTRA</span>
    </div>
  );
}