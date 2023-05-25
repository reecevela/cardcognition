import tcgplayerLogo from "../images/TCGplayer-logo.png";

function Footer() {
    return (
        <footer className="footer">
            <p>
                Copyright {
                    new Date().getFullYear()
                } Reece Vela - All Rights Reserved
            </p>
            <img src={tcgplayerLogo} alt="TCGplayer Logo" />
        </footer>
    )
}

export default Footer