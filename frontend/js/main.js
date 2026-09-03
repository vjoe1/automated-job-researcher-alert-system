/* ============ INIT ============ */
gsap.registerPlugin(ScrollTrigger);

document.getElementById("telegramTopbarLink").href = TELEGRAM_BOT_URL;
document.getElementById("telegramHeroLink").href = TELEGRAM_BOT_URL;
playBootSequence();
playRadarLoop();
fetchJobCount();
fetchJobs();
