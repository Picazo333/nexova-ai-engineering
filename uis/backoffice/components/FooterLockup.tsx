export function FooterLockup() {
  return (
    <footer className="site-footer">
      <div className="wrap">
        <p className="credit">
          Crédito visual del encargo académico. No indica una asociación oficial.
        </p>
        <div className="footer-lockup">
          <div className="lockup-frame lockup-frame-stacked">
            <img
              src="/brand/lockups/signal-stacked.svg"
              alt="4Geeks por Divinivid"
              width={280}
              height={140}
            />
          </div>
          <div className="lockup-frame lockup-frame-wide">
            <img
              src="/brand/lockups/signal-horizontal.svg"
              alt="4Geeks por Divinivid"
              width={400}
              height={64}
            />
          </div>
        </div>
      </div>
    </footer>
  );
}
