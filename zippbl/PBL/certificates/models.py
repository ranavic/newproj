from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

from users.models import User
from courses.models import Course

class CertificateTemplate(models.Model):
    """
    Certificate design templates
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    html_template = models.TextField(help_text='HTML template with placeholders for certificate data')
    css_styles = models.TextField(help_text='CSS styles for the certificate template')
    preview_image = models.ImageField(upload_to='certificate_templates/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Certificate(models.Model):
    """
    Certificates issued to users
    """
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    )
    
    certificate_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    template = models.ForeignKey(CertificateTemplate, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    issue_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    blockchain_verified = models.BooleanField(default=False)
    blockchain_tx_hash = models.CharField(max_length=255, blank=True, null=True, help_text='Blockchain transaction hash')
    blockchain_verification_url = models.URLField(blank=True, null=True)
    pdf_file = models.FileField(upload_to='certificates_pdf/', blank=True, null=True)
    issuer_name = models.CharField(max_length=100, default='SkillForge')
    issuer_signature = models.ImageField(upload_to='certificate_signatures/', blank=True, null=True)
    additional_metadata = models.JSONField(default=dict, blank=True)
    revocation_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"Certificate {self.certificate_id} for {self.user.username}"
    
    @property
    def is_valid(self):
        if self.status != 'issued':
            return False
        if self.expiry_date and timezone.now() > self.expiry_date:
            return False
        return True
    
    def revoke(self, reason):
        self.status = 'revoked'
        self.revocation_reason = reason
        self.save()

class BlockchainCredential(models.Model):
    """
    Blockchain credential records
    """
    BLOCKCHAIN_NETWORKS = (
        ('ethereum', 'Ethereum'),
        ('polygon', 'Polygon'),
        ('binance', 'Binance Smart Chain'),
        ('solana', 'Solana'),
        ('ipfs', 'IPFS'),
    )
    
    certificate = models.OneToOneField(Certificate, on_delete=models.CASCADE, related_name='blockchain_credential')
    network = models.CharField(max_length=20, choices=BLOCKCHAIN_NETWORKS, default='ethereum')
    transaction_hash = models.CharField(max_length=255)
    block_number = models.PositiveIntegerField(null=True, blank=True)
    ipfs_hash = models.CharField(max_length=255, blank=True, null=True, help_text='IPFS hash for certificate data')
    transaction_date = models.DateTimeField(default=timezone.now)
    credential_json = models.JSONField(default=dict, help_text='Full JSON data stored on blockchain')
    verification_attempts = models.PositiveIntegerField(default=0)
    last_verified = models.DateTimeField(null=True, blank=True)
    is_valid = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Blockchain Credential for {self.certificate.certificate_id}"

class VerificationRecord(models.Model):
    """
    Records of certificate verification attempts
    """
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='verification_records')
    verification_date = models.DateTimeField(auto_now_add=True)
    verification_method = models.CharField(max_length=50)
    was_valid = models.BooleanField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    verifier_name = models.CharField(max_length=100, blank=True, null=True)
    verifier_email = models.EmailField(blank=True, null=True)
    verifier_organization = models.CharField(max_length=100, blank=True, null=True)
    additional_data = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"Verification of {self.certificate.certificate_id} on {self.verification_date}"

class CertificationAuthority(models.Model):
    """
    Trusted certificate authorities
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    website = models.URLField()
    logo = models.ImageField(upload_to='certification_authorities/')
    public_key = models.TextField(help_text='Public key for verification')
    is_active = models.BooleanField(default=True)
    contract_address = models.CharField(max_length=255, blank=True, null=True, help_text='Blockchain contract address')
    blockchain_network = models.CharField(max_length=20, choices=BlockchainCredential.BLOCKCHAIN_NETWORKS, default='ethereum')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('certification authority')
        verbose_name_plural = _('certification authorities')
    
    def __str__(self):
        return self.name
