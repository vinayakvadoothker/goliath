import centraLogoImg from "figma:asset/13e993af34fe65754cbc14c91a3cdb0b4df127d6.png";

export function CentraLogo() {
  const logoSrc = typeof centraLogoImg === 'string' ? centraLogoImg : centraLogoImg.src || centraLogoImg;
  
  return (
    <div className="flex flex-col items-center gap-3">
      <div className="w-16 h-16 flex items-center justify-center">
        <img 
          src={logoSrc as string} 
          alt="Centra Logo"
          className="w-full h-full object-contain"
        />
      </div>
      <span className="text-white text-xl tracking-wider">CENTRA</span>
    </div>
  );
}