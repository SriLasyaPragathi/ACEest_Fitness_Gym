import jenkins.model.Jenkins
import hudson.security.HudsonPrivateSecurityRealm
import hudson.security.FullControlOnceLoggedInAuthorizationStrategy
import org.jenkinsci.plugins.matrixauth.authorization.MatrixAuthorizationStrategy

println("=== Initializing Jenkins Security ===")

def instance = Jenkins.getInstance()

try {
    // Disable CSRF protection
    System.setProperty("hudson.security.csrf.GlobalCrumbIssuerConfiguration.DISABLE_CSRF_PROTECTION", "true")
    
    // Create security realm
    def hudsonRealm = new HudsonPrivateSecurityRealm(false)
    
    // Create admin user with admin/admin
    hudsonRealm.createAccount("admin", "admin")
    
    instance.setSecurityRealm(hudsonRealm)
    
    // Set matrix-based authorization
    def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
    instance.setAuthorizationStrategy(strategy)
    
    instance.save()
    println("✓ Jenkins security configured: admin/admin")
} catch (Exception e) {
    println("✗ Error during security setup: ${e.message}")
    e.printStackTrace()
}

println("=== Jenkins Initialization Complete ===")

