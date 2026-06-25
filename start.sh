# start.sh — Start the MITIC Ratings API server + optional frontend dev server
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

case "${1:-help}" in
  dev)
    echo "Starting API server on :3001 and frontend dev on :5173..."
    node api/server.mjs &
    API_PID=$!
    cd frontend && npm run dev &
    FRONTEND_PID=$!
    trap "kill $API_PID $FRONTEND_PID 2>/dev/null" EXIT
    wait
    ;;
  api)
    echo "Starting API server on :3001..."
    node api/server.mjs
    ;;
  scrape)
    echo "Scraping MITIC ratings from airhockeyrank.com..."
    python3 archive.py --db "$SCRIPT_DIR/mitic.db"
    ;;
  test)
    echo "Running tests..."
    python3 test.py
    ;;
    echo "Building static JSON data..."
    python3 build-static.py
    echo "Building frontend..."
    cd frontend && npm run build
    echo "Static site ready at frontend/dist/"
    ;;
  static)
    echo "Building static JSON + frontend for GitHub Pages..."
    python3 build-static.py
    cd frontend && npm run build
    echo ""
    echo "Static site built at frontend/dist/."
    echo "You can serve it locally with:  python3 -m http.server 3002 -d frontend/dist"
    echo "Or just push to GitHub and the Actions workflow will deploy to Pages."
    ;;
  prod)
    echo "Building frontend and starting production server on :3001..."
    cd frontend && npm run build
    cd ..
    node api/server.mjs
    ;;
  *)
    echo "Usage: $0 {dev|api|scrape|build|prod}"
    echo ""
    echo "  dev     Start API + frontend dev server (hot reload)"
    echo "  api     Start only the API server on :3001"
    echo "  scrape  Fetch latest MITIC data from airhockeyrank.com"
    echo "  build   Build the frontend for production"
    echo "  prod    Build frontend + start production server on :3001"
    ;;
esac
