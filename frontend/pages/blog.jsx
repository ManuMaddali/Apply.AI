"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { 
  FileText, 
  Plus, 
  User, 
  Calendar, 
  MessageCircle, 
  Heart, 
  Share2,
  TrendingUp,
  Award,
  Briefcase,
  CheckCircle,
  Clock,
  Target,
  Star,
  Filter,
  Search,
  BookOpen,
  Users,
  ArrowRight,
  ThumbsUp,
  Eye,
  PenTool,
  LogOut
} from "lucide-react"
import { useState, useEffect } from "react"
import { useAuth } from '../contexts/AuthContext'

export default function BlogPage() {
  const { isAuthenticated, user, logout } = useAuth()
  const [posts, setPosts] = useState([])
  const [filterCategory, setFilterCategory] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [showNewPostForm, setShowNewPostForm] = useState(false)
  const [newPost, setNewPost] = useState({
    title: '',
    content: '',
    category: 'success-story',
    author: '',
    company: '',
    position: ''
  })

  const handleLogout = async () => {
    await logout()
  }

  // Load posts from localStorage on component mount
  useEffect(() => {
    const savedPosts = localStorage.getItem('applyai_blog_posts')
    if (savedPosts) {
      setPosts(JSON.parse(savedPosts))
    } else {
      // Initialize with some sample posts
      const samplePosts = [
        {
          id: 1,
          title: "How ApplyAI Helped Me Land My Dream Job at Google",
          content: "After months of job hunting, I was getting frustrated with generic resumes. ApplyAI helped me tailor my resume for each application, and within 2 weeks I got an interview at Google. The tailored resume highlighted exactly what they were looking for!",
          category: "success-story",
          author: "Sarah Chen",
          company: "Google",
          position: "Software Engineer",
          date: "2024-01-15",
          likes: 24,
          comments: 8,
          views: 156
        },
        {
          id: 2,
          title: "Interview Tomorrow - Thanks to ApplyAI!",
          content: "I have an interview tomorrow at Microsoft for a Product Manager role. ApplyAI's resume tailoring emphasized my data analysis skills and product experience perfectly. Feeling confident!",
          category: "interview-update",
          author: "Alex Rodriguez",
          company: "Microsoft",
          position: "Product Manager",
          date: "2024-01-18",
          likes: 12,
          comments: 3,
          views: 89
        },
        {
          id: 3,
          title: "Resume Tailoring Tips That Actually Work",
          content: "After using ApplyAI for 20+ applications, here are the key things I learned: 1) Always match keywords from the job description 2) Quantify your achievements 3) Emphasize relevant skills for each role. My interview rate went from 5% to 40%!",
          category: "tips-advice",
          author: "Michael Kim",
          company: "Various",
          position: "Data Scientist",
          date: "2024-01-12",
          likes: 45,
          comments: 12,
          views: 234
        },
        {
          id: 4,
          title: "Career Transition Success: From Marketing to Tech",
          content: "I was worried about transitioning from marketing to tech. ApplyAI helped me highlight transferable skills and tailor my resume for each tech role. Just got hired as a Technical Product Manager!",
          category: "career-change",
          author: "Emily Johnson",
          company: "Stripe",
          position: "Technical Product Manager",
          date: "2024-01-10",
          likes: 33,
          comments: 15,
          views: 198
        }
      ]
      setPosts(samplePosts)
      localStorage.setItem('applyai_blog_posts', JSON.stringify(samplePosts))
    }
  }, [])

  // Save posts to localStorage whenever posts change
  useEffect(() => {
    if (posts.length > 0) {
      localStorage.setItem('applyai_blog_posts', JSON.stringify(posts))
    }
  }, [posts])

  const handleSubmitPost = (e) => {
    e.preventDefault()
    if (!newPost.title || !newPost.content || !newPost.author) {
      alert('Please fill in all required fields')
      return
    }

    const post = {
      id: Date.now(),
      ...newPost,
      date: new Date().toISOString().split('T')[0],
      likes: 0,
      comments: 0,
      views: 0
    }

    setPosts([post, ...posts])
    setNewPost({
      title: '',
      content: '',
      category: 'success-story',
      author: '',
      company: '',
      position: ''
    })
    setShowNewPostForm(false)
  }

  const filteredPosts = posts.filter(post => {
    const matchesCategory = filterCategory === 'all' || post.category === filterCategory
    const matchesSearch = post.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         post.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         post.author.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesCategory && matchesSearch
  })

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'success-story': return <Award className="h-4 w-4" />
      case 'interview-update': return <Briefcase className="h-4 w-4" />
      case 'tips-advice': return <BookOpen className="h-4 w-4" />
      case 'career-change': return <TrendingUp className="h-4 w-4" />
      default: return <MessageCircle className="h-4 w-4" />
    }
  }

  const getCategoryColor = (category) => {
    switch (category) {
      case 'success-story': return 'bg-green-100 text-green-800'
      case 'interview-update': return 'bg-blue-100 text-blue-800'
      case 'tips-advice': return 'bg-purple-100 text-purple-800'
      case 'career-change': return 'bg-orange-100 text-orange-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatCategoryName = (category) => {
    switch (category) {
      case 'success-story': return 'Success Story'
      case 'interview-update': return 'Interview Update'
      case 'tips-advice': return 'Tips & Advice'
      case 'career-change': return 'Career Change'
      default: return category
    }
  }

  return (
    <div className="flex min-h-[100dvh] flex-col bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="px-4 lg:px-6 h-16 flex items-center justify-between border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <Link className="flex items-center gap-2 font-semibold" href="/">
          <FileText className="h-6 w-6 text-blue-600" />
          <span>ApplyAI</span>
        </Link>
        <nav className="hidden md:flex gap-6">
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/">
            Home
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/features">
            Features
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/how-it-works">
            How It Works
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/faq">
            FAQ
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/about">
            About
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4 text-blue-600" href="/blog">
            Blog
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/contact">
            Contact
          </Link>
        </nav>
        <div className="hidden md:flex gap-4">
          {isAuthenticated ? (
            <>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                  <User className="h-4 w-4 text-white" />
                </div>
                <span className="text-sm font-medium">{user?.full_name || user?.email}</span>
              </div>
              <Link href="/app">
                <Button variant="outline">Dashboard</Button>
              </Link>
              <Button variant="outline" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                Sign Out
              </Button>
            </>
          ) : (
            <>
              <Link href="/login">
                <Button variant="outline">Log In</Button>
              </Link>
              <Link href="/register">
                <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">Sign Up Free</Button>
              </Link>
            </>
          )}
        </div>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="w-full py-12 md:py-16">
          <div className="container px-4 md:px-6">
            <div className="text-center max-w-4xl mx-auto">
              <div className="inline-block rounded-lg bg-gradient-to-r from-blue-100 to-purple-100 px-3 py-1 text-sm text-blue-800 mb-4">
                <Users className="inline h-4 w-4 mr-1" />
                Community Stories
              </div>
              <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
                Resume Success Stories & Interview Updates
              </h1>
              <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
                Share your journey, celebrate your wins, and help others succeed. Real stories from real users about how ApplyAI helped them land their dream jobs.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button 
                  onClick={() => setShowNewPostForm(true)}
                  className="gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  <Plus className="h-4 w-4" />
                  Share Your Story
                </Button>
                <Button variant="outline" className="gap-2">
                  <BookOpen className="h-4 w-4" />
                  Read Success Stories
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* New Post Form */}
        {showNewPostForm && (
          <section className="w-full py-8 bg-white/80 backdrop-blur-sm border-y">
            <div className="container px-4 md:px-6">
              <div className="max-w-2xl mx-auto">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <PenTool className="h-5 w-5" />
                      Share Your Story
                    </CardTitle>
                    <CardDescription>
                      Tell the community about your experience with ApplyAI, interview updates, or job search tips.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handleSubmitPost} className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium mb-1">Your Name *</label>
                          <input
                            type="text"
                            value={newPost.author}
                            onChange={(e) => setNewPost({...newPost, author: e.target.value})}
                            className="w-full p-2 border rounded-md"
                            placeholder="John Doe"
                            required
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-1">Category *</label>
                          <select
                            value={newPost.category}
                            onChange={(e) => setNewPost({...newPost, category: e.target.value})}
                            className="w-full p-2 border rounded-md"
                            required
                          >
                            <option value="success-story">Success Story</option>
                            <option value="interview-update">Interview Update</option>
                            <option value="tips-advice">Tips & Advice</option>
                            <option value="career-change">Career Change</option>
                          </select>
                        </div>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium mb-1">Company</label>
                          <input
                            type="text"
                            value={newPost.company}
                            onChange={(e) => setNewPost({...newPost, company: e.target.value})}
                            className="w-full p-2 border rounded-md"
                            placeholder="Google, Microsoft, etc."
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-1">Position</label>
                          <input
                            type="text"
                            value={newPost.position}
                            onChange={(e) => setNewPost({...newPost, position: e.target.value})}
                            className="w-full p-2 border rounded-md"
                            placeholder="Software Engineer, Product Manager, etc."
                          />
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1">Title *</label>
                        <input
                          type="text"
                          value={newPost.title}
                          onChange={(e) => setNewPost({...newPost, title: e.target.value})}
                          className="w-full p-2 border rounded-md"
                          placeholder="How ApplyAI helped me land my dream job..."
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1">Your Story *</label>
                        <textarea
                          value={newPost.content}
                          onChange={(e) => setNewPost({...newPost, content: e.target.value})}
                          className="w-full p-2 border rounded-md h-32"
                          placeholder="Share your experience with ApplyAI, interview updates, tips, or success story..."
                          required
                        />
                      </div>
                      <div className="flex gap-2">
                        <Button type="submit" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                          Post Story
                        </Button>
                        <Button type="button" variant="outline" onClick={() => setShowNewPostForm(false)}>
                          Cancel
                        </Button>
                      </div>
                    </form>
                  </CardContent>
                </Card>
              </div>
            </div>
          </section>
        )}

        {/* Filters and Search */}
        <section className="w-full py-8 bg-white/60 backdrop-blur-sm">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col md:flex-row gap-4 justify-between items-center max-w-4xl mx-auto">
              <div className="flex flex-wrap gap-2">
                <Button
                  variant={filterCategory === 'all' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilterCategory('all')}
                >
                  All Posts
                </Button>
                <Button
                  variant={filterCategory === 'success-story' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilterCategory('success-story')}
                  className="gap-1"
                >
                  <Award className="h-3 w-3" />
                  Success Stories
                </Button>
                <Button
                  variant={filterCategory === 'interview-update' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilterCategory('interview-update')}
                  className="gap-1"
                >
                  <Briefcase className="h-3 w-3" />
                  Interview Updates
                </Button>
                <Button
                  variant={filterCategory === 'tips-advice' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilterCategory('tips-advice')}
                  className="gap-1"
                >
                  <BookOpen className="h-3 w-3" />
                  Tips & Advice
                </Button>
                <Button
                  variant={filterCategory === 'career-change' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilterCategory('career-change')}
                  className="gap-1"
                >
                  <TrendingUp className="h-3 w-3" />
                  Career Change
                </Button>
              </div>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search posts..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border rounded-md min-w-64"
                />
              </div>
            </div>
          </div>
        </section>

        {/* Blog Posts */}
        <section className="w-full py-12">
          <div className="container px-4 md:px-6">
            <div className="max-w-4xl mx-auto">
              {filteredPosts.length === 0 ? (
                <div className="text-center py-12">
                  <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-600 mb-2">No posts found</h3>
                  <p className="text-gray-500 mb-4">
                    {searchTerm ? 'Try adjusting your search terms.' : 'Be the first to share your story!'}
                  </p>
                  <Button 
                    onClick={() => setShowNewPostForm(true)}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                  >
                    Share Your Story
                  </Button>
                </div>
              ) : (
                <div className="space-y-6">
                  {filteredPosts.map((post) => (
                    <Card key={post.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            <div className="bg-gradient-to-r from-blue-100 to-purple-100 p-2 rounded-full">
                              <User className="h-4 w-4 text-blue-600" />
                            </div>
                            <div>
                              <p className="font-semibold text-gray-900">{post.author}</p>
                              <p className="text-sm text-gray-500">
                                {post.position && post.company ? `${post.position} at ${post.company}` : 
                                 post.company || post.position || 'ApplyAI User'}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(post.category)}`}>
                              {getCategoryIcon(post.category)}
                              {formatCategoryName(post.category)}
                            </span>
                            <span className="text-sm text-gray-500 flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {new Date(post.date).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">{post.title}</h3>
                        <p className="text-gray-600 mb-4 leading-relaxed">{post.content}</p>
                        <div className="flex items-center gap-6 text-sm text-gray-500 pt-3 border-t">
                          <button className="flex items-center gap-1 hover:text-blue-600 transition-colors">
                            <ThumbsUp className="h-4 w-4" />
                            {post.likes}
                          </button>
                          <button className="flex items-center gap-1 hover:text-blue-600 transition-colors">
                            <MessageCircle className="h-4 w-4" />
                            {post.comments}
                          </button>
                          <span className="flex items-center gap-1">
                            <Eye className="h-4 w-4" />
                            {post.views}
                          </span>
                          <button className="flex items-center gap-1 hover:text-blue-600 transition-colors ml-auto">
                            <Share2 className="h-4 w-4" />
                            Share
                          </button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="w-full py-16 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
          <div className="container px-4 md:px-6">
            <div className="text-center max-w-3xl mx-auto">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to Write Your Success Story?</h2>
              <p className="text-xl text-blue-100 mb-8">
                Join thousands of job seekers who have used ApplyAI to land their dream jobs and boost their career.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/app">
                  <Button size="lg" className="gap-2 bg-white text-blue-600 hover:bg-blue-50">
                    <Target className="h-5 w-5" />
                    Try ApplyAI Free
                  </Button>
                </Link>
                <Button 
                  size="lg" 
                  variant="outline" 
                  className="gap-2 border-white text-white hover:bg-white/10"
                  onClick={() => setShowNewPostForm(true)}
                >
                  <Plus className="h-5 w-5" />
                  Share Your Story
                </Button>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t bg-white/80 backdrop-blur-sm">
        <div className="container px-4 md:px-6 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              <span className="font-semibold">ApplyAI</span>
            </div>
            <div className="flex gap-6">
              <Link className="text-sm text-gray-600 hover:text-blue-600" href="/features">
                Features
              </Link>
              <Link className="text-sm text-gray-600 hover:text-blue-600" href="/how-it-works">
                How It Works
              </Link>
              <Link className="text-sm text-gray-600 hover:text-blue-600" href="/faq">
                FAQ
              </Link>
              <Link className="text-sm text-gray-600 hover:text-blue-600" href="/about">
                About
              </Link>
              <Link className="text-sm text-gray-600 hover:text-blue-600" href="/blog">
                Blog
              </Link>
            </div>
            <p className="text-sm text-gray-600">
              © 2024 ApplyAI. Built with ❤️ for job seekers.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
} 